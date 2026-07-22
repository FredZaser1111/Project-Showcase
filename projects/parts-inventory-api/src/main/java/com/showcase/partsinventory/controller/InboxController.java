package com.showcase.partsinventory.controller;

import com.showcase.partsinventory.repository.ApprovalQueueRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class InboxController {

    private final ApprovalQueueRepository approvals;

    public InboxController(ApprovalQueueRepository approvals) {
        this.approvals = approvals;
    }

    @GetMapping({"/", "/inbox"})
    public String inbox(Model model) {
        model.addAttribute("approvals", approvals.listOpen());
        model.addAttribute("title", "HITL Approval Inbox");
        return "inbox";
    }
}
