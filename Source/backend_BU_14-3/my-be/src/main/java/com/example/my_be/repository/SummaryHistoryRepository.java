package com.example.my_be.repository;

import com.example.my_be.model.SummaryHistory;
import com.example.my_be.model.SummarySession;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SummaryHistoryRepository extends JpaRepository<SummaryHistory, Long> {
    // You can add custom queries if necessary
    List<SummaryHistory> findBySession(SummarySession session); // Add this
}
