package com.example.my_be.service;

import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.model.MasGoal;
import com.example.my_be.model.MasSession;
import com.example.my_be.repository.MasGoalRepository;
import com.example.my_be.repository.MasSessionRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MasGoalService {

    @Autowired
    private MasGoalRepository masGoalRepository;

    @Autowired
    private MasSessionRepository masSessionRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Lưu current goal_state (nếu có) vào mas_goals.
     */
    public MasGoal createFromState(String sessionId, String goalStateJson) {
        if (goalStateJson == null || goalStateJson.isEmpty() || "{}".equals(goalStateJson)) {
            return null;
        }

        try {
            JsonNode node = objectMapper.readTree(goalStateJson);
            if (node == null || node.isMissingNode() || node.isEmpty()) {
                return null;
            }

            MasSession session = masSessionRepository.findById(sessionId)
                .orElseThrow(() -> new RuntimeException("MasSession not found: " + sessionId));

            MasGoal goal = new MasGoal();
            goal.setGoalId(UUID.randomUUID().toString());
            goal.setSession(session);

            // Map tối thiểu từ GoalState.py
            // Nếu không có "type" trong JSON, dùng default "summarization"
            String type = node.path("type").asText(null);
            if (type == null || type.isEmpty()) {
                type = "summarization";
            }
            goal.setGoalType(type);
            goal.setDescription(node.path("description").asText(null));

            JsonNode reqNode = node.path("requirements");
            goal.setRequirements(reqNode.isMissingNode() ? null : reqNode.toString());

            int priority = node.path("priority").asInt(5);
            goal.setPriority(priority);

            String statusStr = node.path("status").asText(null);
            if (statusStr != null && !statusStr.isEmpty()) {
                // GoalState dùng lowercase: pending, in_progress, achieved, cancelled
                String upper = statusStr.trim().toUpperCase();
                // Map đơn giản: PENDING, IN_PROGRESS, ACHIEVED, FAILED, CANCELLED
                if ("ACHIEVED".equals(upper) || "COMPLETED".equals(upper)) {
                    goal.setStatus(MasGoal.GoalStatus.ACHIEVED);
                } else if ("IN_PROGRESS".equals(upper)) {
                    goal.setStatus(MasGoal.GoalStatus.IN_PROGRESS);
                } else if ("CANCELLED".equals(upper)) {
                    goal.setStatus(MasGoal.GoalStatus.CANCELLED);
                } else {
                    goal.setStatus(MasGoal.GoalStatus.PENDING);
                }
            }

            return masGoalRepository.save(goal);
        } catch (Exception e) {
            // Nếu parse lỗi thì bỏ qua để không làm hỏng flow chính
            System.err.println("[WARN] Failed to parse goal_state for mas_goals: " + e.getMessage());
            return null;
        }
    }
}

