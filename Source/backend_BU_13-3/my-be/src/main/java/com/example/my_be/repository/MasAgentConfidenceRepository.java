package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.MasAgentConfidence;

@Repository
public interface MasAgentConfidenceRepository extends JpaRepository<MasAgentConfidence, String> {
    List<MasAgentConfidence> findByAgentAgentId(String agentId);
    List<MasAgentConfidence> findByAgentAgentIdAndTaskType(String agentId, String taskType);
    Optional<MasAgentConfidence> findFirstByAgentAgentIdAndTaskTypeOrderByCreatedAtDesc(String agentId, String taskType);
    List<MasAgentConfidence> findBySessionSessionId(String sessionId);
}
