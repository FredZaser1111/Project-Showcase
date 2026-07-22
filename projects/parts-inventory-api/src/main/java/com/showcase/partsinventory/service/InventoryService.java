package com.showcase.partsinventory.service;

import com.showcase.partsinventory.model.MovementRequest;
import com.showcase.partsinventory.model.PartInventory;
import com.showcase.partsinventory.model.StockMovement;
import com.showcase.partsinventory.repository.PartRepository;
import com.showcase.partsinventory.repository.StockMovementRepository;
import com.showcase.partsinventory.repository.WorkflowEventRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * Stock level changes always append a movement row first, then update stock_levels in the same TX.
 */
@Service
public class InventoryService {

    private static final Set<String> TYPES = Set.of("RECEIPT", "RESERVE", "ISSUE", "ADJUST");

    private final PartRepository parts;
    private final StockMovementRepository movements;
    private final WorkflowEventRepository events;

    public InventoryService(
            PartRepository parts,
            StockMovementRepository movements,
            WorkflowEventRepository events
    ) {
        this.parts = parts;
        this.movements = movements;
        this.events = events;
    }

    public List<PartInventory> listParts() {
        return parts.findAll();
    }

    public PartInventory getPart(String partKey) {
        return parts.findByKey(partKey)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown part: " + partKey));
    }

    public List<StockMovement> listMovements(String partKey) {
        return movements.findAll(partKey);
    }

    @Transactional
    public StockMovement appendMovement(MovementRequest request) {
        String type = request.type().trim().toUpperCase(Locale.ROOT);
        if (!TYPES.contains(type)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "type must be one of " + TYPES);
        }
        if (parts.findByKey(request.partKey()).isEmpty()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown part: " + request.partKey());
        }

        int current = parts.lockQty(request.partKey());
        int delta = switch (type) {
            case "RECEIPT", "ADJUST" -> request.qty();
            case "RESERVE", "ISSUE" -> -request.qty();
            default -> throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Unsupported type");
        };
        // ADJUST with negative intent: callers should pass positive qty and use ISSUE/RESERVE;
        // for ADJUST we treat qty as signed via optional negative — keep positive-only API.
        int newBalance = current + delta;
        if (newBalance < 0) {
            throw new ResponseStatusException(
                    HttpStatus.CONFLICT,
                    "Insufficient stock: on_hand=" + current + ", need=" + request.qty()
            );
        }

        StockMovement movement = movements.append(
                request.partKey(),
                type,
                delta,
                newBalance,
                request.caseId(),
                request.reason()
        );
        parts.updateQty(request.partKey(), newBalance);
        events.append(
                "stock_movement_" + type.toLowerCase(Locale.ROOT),
                request.partKey(),
                request.caseId(),
                Map.of(
                        "movement_id", movement.movementId().toString(),
                        "qty_delta", delta,
                        "balance_after", newBalance
                )
        );
        return movement;
    }
}
