package com.example.my_be.controller;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.my_be.dto.SummaryDifficultyAdjustmentDTO;
import com.example.my_be.service.SummaryDifficultyAdjustmentService;

@RestController
@RequestMapping("/api/summary-difficulty-adjustments")
public class SummaryDifficultyAdjustmentController {

    @Autowired
    private SummaryDifficultyAdjustmentService summaryDifficultyAdjustmentService;

    @PostMapping
    public ResponseEntity<SummaryDifficultyAdjustmentDTO> create(@RequestBody SummaryDifficultyAdjustmentDTO request) {
        SummaryDifficultyAdjustmentDTO created = summaryDifficultyAdjustmentService.create(request);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }

    @GetMapping("/{id}")
    public ResponseEntity<SummaryDifficultyAdjustmentDTO> getById(@PathVariable Long id) {
        Optional<SummaryDifficultyAdjustmentDTO> item = summaryDifficultyAdjustmentService.getById(id);
        return item.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @GetMapping
    public ResponseEntity<List<SummaryDifficultyAdjustmentDTO>> getBySummaryId(
            @RequestParam(required = false) String summaryId,
            @RequestParam(required = false) String userId) {
        if (summaryId != null && !summaryId.isBlank()) {
            return ResponseEntity.ok(summaryDifficultyAdjustmentService.getBySummaryId(summaryId));
        }
        if (userId != null && !userId.isBlank()) {
            return ResponseEntity.ok(summaryDifficultyAdjustmentService.getByUserId(userId));
        }
        return ResponseEntity.badRequest().build();
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        summaryDifficultyAdjustmentService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
