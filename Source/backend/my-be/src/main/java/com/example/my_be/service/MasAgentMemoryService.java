package com.example.my_be.service;

import java.util.Iterator;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.model.Agent;
import com.example.my_be.model.Agent.AgentType;
import com.example.my_be.model.MasAgentMemory;
import com.example.my_be.repository.MasAgentMemoryRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MasAgentMemoryService {

    @Autowired
    private MasAgentMemoryRepository masAgentMemoryRepository;

    @Autowired
    private AgentService agentService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Lưu agent_memories (nếu serialize được) vào mas_agent_memories.
     * Hiện tại chỉ lưu context/raw JSON cho từng agent; input/output có thể được mở rộng sau.
     */
    public void createFromState(String agentMemoriesJson, String taskType) {
        if (agentMemoriesJson == null || agentMemoriesJson.isEmpty() || "{}".equals(agentMemoriesJson)) {
            return;
        }

        try {
            JsonNode root = objectMapper.readTree(agentMemoriesJson);
            if (root == null || !root.isObject() || root.isEmpty()) {
                return;
            }

            Iterator<String> names = root.fieldNames();
            while (names.hasNext()) {
                String agentName = names.next();
                JsonNode memNode = root.path(agentName);

                AgentType type = mapAgentNameToType(agentName);
                if (type == null) {
                    continue;
                }

                Agent agent = agentService.getAgentByType(type).orElse(null);
                if (agent == null) {
                    continue;
                }

                MasAgentMemory mem = new MasAgentMemory();
                mem.setMemoryId(UUID.randomUUID().toString());
                mem.setAgent(agent);
                mem.setTaskType(taskType);
                // Để đơn giản, lưu toàn bộ JSON của agent memory vào context
                mem.setContext(memNode.toString());
                mem.setInputData(null);
                mem.setOutputData(null);
                mem.setSuccess(true);

                masAgentMemoryRepository.save(mem);
            }
        } catch (Exception e) {
            System.err.println("[WARN] Failed to parse agent_memories for mas_agent_memories: " + e.getMessage());
        }
    }

    private AgentType mapAgentNameToType(String agentName) {
        if (agentName == null) return null;
        switch (agentName) {
            case "planning_agent":
                return AgentType.PLANNING;
            case "abstracter_agent":
            case "abstractive_agent":
                return AgentType.ABSTRACTER;
            case "extractor_agent":
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

