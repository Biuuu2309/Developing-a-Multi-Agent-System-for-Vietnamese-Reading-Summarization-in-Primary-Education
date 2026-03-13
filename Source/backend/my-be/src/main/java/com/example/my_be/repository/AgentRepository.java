package com.example.my_be.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.Agent;
import com.example.my_be.model.Agent.AgentType;

@Repository
public interface AgentRepository extends JpaRepository<Agent, String> {
    Optional<Agent> findByAgentTypeAndIsActiveTrue(AgentType agentType);
}

