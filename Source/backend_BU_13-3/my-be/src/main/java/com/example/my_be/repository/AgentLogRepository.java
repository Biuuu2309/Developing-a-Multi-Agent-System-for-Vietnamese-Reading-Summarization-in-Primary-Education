package com.example.my_be.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.AgentLog;

@Repository
public interface AgentLogRepository extends JpaRepository<AgentLog, String> {
    List<AgentLog> findByMessageId(String messageId);
    List<AgentLog> findByAgentId(String agentId);
}

