package com.example.my_be.repository;

import com.example.my_be.model.SummarySession;
import com.example.my_be.model.User;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SummarySessionRepository extends JpaRepository<SummarySession, Long> {
    // You can add custom queries if necessary

    Optional<SummarySession> findByCreatedByAndContentHash(User createdBy, String contentHash);

    Optional<SummarySession> findByCreatedByAndContent(User createdBy, String content);
    List<SummarySession> findByCreatedBy(User createdBy); // Add this
}
