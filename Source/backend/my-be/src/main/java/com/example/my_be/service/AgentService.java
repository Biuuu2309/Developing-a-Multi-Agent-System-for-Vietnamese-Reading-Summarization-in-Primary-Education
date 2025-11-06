package com.example.my_be.service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.model.Agent;
import com.example.my_be.repository.AgentRepository;

@Service
public class AgentService {
    @Autowired
    private AgentRepository agentRepository;

    public Agent createAgent(Agent agent) {
        if (agent.getAgentId() == null || agent.getAgentId().isEmpty()) {
            agent.setAgentId(UUID.randomUUID().toString());
        }
        return agentRepository.save(agent);
    }

    public List<Agent> getAllAgents() {
        return agentRepository.findAll();
    }

    public Optional<Agent> getAgentById(String agentId) {
        return agentRepository.findById(agentId);
    }

    public void deleteAgent(String agentId) {
        agentRepository.deleteById(agentId);
    }
}

