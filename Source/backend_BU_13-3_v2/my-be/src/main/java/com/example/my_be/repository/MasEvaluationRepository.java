package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.MasEvaluation;

@Repository
public interface MasEvaluationRepository extends JpaRepository<MasEvaluation, String> {
    List<MasEvaluation> findByStateStateId(String stateId);
    Optional<MasEvaluation> findFirstByStateStateIdOrderByCreatedAtDesc(String stateId);
}
