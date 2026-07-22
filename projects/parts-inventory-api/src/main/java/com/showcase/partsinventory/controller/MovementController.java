package com.showcase.partsinventory.controller;

import com.showcase.partsinventory.model.MovementRequest;
import com.showcase.partsinventory.model.StockMovement;
import com.showcase.partsinventory.service.InventoryService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/movements")
public class MovementController {

    private final InventoryService inventory;

    public MovementController(InventoryService inventory) {
        this.inventory = inventory;
    }

    @GetMapping
    public List<StockMovement> list(@RequestParam(required = false) String partKey) {
        return inventory.listMovements(partKey);
    }

    @PostMapping
    public StockMovement append(@Valid @RequestBody MovementRequest request) {
        return inventory.appendMovement(request);
    }
}
