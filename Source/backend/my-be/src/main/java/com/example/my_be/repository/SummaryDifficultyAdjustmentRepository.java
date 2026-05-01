package com.example.my_be.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.SummaryDifficultyAdjustment;

@Repository
public interface SummaryDifficultyAdjustmentRepository extends JpaRepository<SummaryDifficultyAdjustment, Long> {
    List<SummaryDifficultyAdjustment> findBySummaryIdRefOrderByCreatedAtDesc(String summaryId);

    List<SummaryDifficultyAdjustment> findByCreatedByUserIdRefOrderByCreatedAtDesc(String userId);
}
