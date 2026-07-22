package com.showcase.partsinventory.controller;

import com.showcase.partsinventory.model.PurchaseOrder;
import com.showcase.partsinventory.model.ReserveOrOrderRequest;
import com.showcase.partsinventory.model.ReserveOrOrderResponse;
import com.showcase.partsinventory.service.WorkflowService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api")
public class WorkflowController {

    private final WorkflowService workflows;

    public WorkflowController(WorkflowService workflows) {
        this.workflows = workflows;
    }

    @PostMapping("/workflows/reserve-or-order")
    public ReserveOrOrderResponse reserveOrOrder(@Valid @RequestBody ReserveOrOrderRequest request) {
        return workflows.reserveOrOrder(request);
    }

    @GetMapping("/purchase-orders")
    public List<PurchaseOrder> purchaseOrders() {
        return workflows.listOpenPurchaseOrders();
    }
}
