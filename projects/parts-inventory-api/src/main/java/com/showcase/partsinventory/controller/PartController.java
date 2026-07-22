package com.showcase.partsinventory.controller;

import com.showcase.partsinventory.model.PartInventory;
import com.showcase.partsinventory.service.InventoryService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/parts")
public class PartController {

    private final InventoryService inventory;

    public PartController(InventoryService inventory) {
        this.inventory = inventory;
    }

    @GetMapping
    public List<Map<String, Object>> list() {
        return inventory.listParts().stream().map(this::toAgentShape).toList();
    }

    @GetMapping("/{partKey}")
    public Map<String, Object> get(@PathVariable String partKey) {
        return toAgentShape(inventory.getPart(partKey));
    }

    /** Matches predictive-maintenance-agent check_inventory response keys. */
    private Map<String, Object> toAgentShape(PartInventory p) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("part_key", p.partKey());
        m.put("found", p.found());
        m.put("sku", p.sku());
        m.put("qty", p.qty());
        m.put("unit_cost", p.unitCost() == null ? 0 : p.unitCost().doubleValue());
        m.put("supplier", p.supplier());
        m.put("in_stock", p.inStock());
        m.put("description", p.description());
        m.put("reorder_point", p.reorderPoint());
        return m;
    }
}
