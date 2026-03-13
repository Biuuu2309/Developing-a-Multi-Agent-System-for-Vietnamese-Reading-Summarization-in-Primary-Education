package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.MasGoal;

@Repository
public interface MasGoalRepository extends JpaRepository<MasGoal, String> {
    List<MasGoal> findBySessionSessionId(String sessionId);
    List<MasGoal> findBySessionSessionIdAndStatus(String sessionId, MasGoal.GoalStatus status);
    Optional<MasGoal> findFirstBySessionSessionIdAndStatusOrderByCreatedAtDesc(String sessionId, MasGoal.GoalStatus status);
}
