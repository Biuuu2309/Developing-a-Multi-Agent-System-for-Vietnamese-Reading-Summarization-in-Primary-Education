package com.example.my_be.service;

import java.math.BigDecimal;
import java.util.Iterator;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.model.Agent;
import com.example.my_be.model.Agent.AgentType;
import com.example.my_be.model.MasAgentConfidence;
import com.example.my_be.model.MasSession;
import com.example.my_be.repository.MasAgentConfidenceRepository;
import com.example.my_be.repository.MasSessionRepository;
import com.fasterxml.jackson.databind.JsonNode;

@Service
public class MasAgentConfidenceService {

    @Autowired
    private MasAgentConfidenceRepository masAgentConfidenceRepository;

    @Autowired
    private MasSessionRepository masSessionRepository;

    @Autowired
    private AgentService agentService;

    /**
     * Lưu agent_confidences vào mas_agent_confidences.
     */
    public void createFromState(String sessionId, JsonNode agentConfs, String taskType) {
        if (agentConfs == null || !agentConfs.isObject()) {
            return;
        }

        MasSession session = masSessionRepository.findById(sessionId)
            .orElseThrow(() -> new RuntimeException("MasSession not found: " + sessionId));

        Iterator<String> fieldNames = agentConfs.fieldNames();
        while (fieldNames.hasNext()) {
            String agentName = fieldNames.next(); // ví dụ: planning_agent, abstractive_agent, extractive_agent, evaluation_agent
            double score = agentConfs.path(agentName).asDouble(0.0);

            AgentType type = mapAgentNameToType(agentName);
            if (type == null) {
                continue;
            }

            Agent agent = agentService.getAgentByType(type).orElse(null);
            if (agent == null) {
                continue;
            }

            MasAgentConfidence conf = new MasAgentConfidence();
            conf.setConfidenceId(UUID.randomUUID().toString());
            conf.setAgent(agent);
            conf.setSession(session);
            conf.setTaskType(taskType);
            conf.setConfidenceScore(BigDecimal.valueOf(score));
            conf.setContext(null);

            masAgentConfidenceRepository.save(conf);
        }
    }

    private AgentType mapAgentNameToType(String agentName) {
        if (agentName == null) return null;
        switch (agentName) {
            case "planning_agent":
                return AgentType.PLANNING;
            case "abstractive_agent":
                return AgentType.ABSTRACTER;
            case "extractive_agent":
                return AgentType.EXTRACTOR;
            case "evaluation_agent":
                return AgentType.EVALUATION;
            case "image2text_agent":
                return AgentType.IMAGE2TEXT;
            case "intent_agent":
                return AgentType.INTENT;
            default:
                return null;
        }
    }
}

