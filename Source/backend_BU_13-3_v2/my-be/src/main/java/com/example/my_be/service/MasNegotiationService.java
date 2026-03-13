package com.example.my_be.service;

import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.model.MasNegotiation;
import com.example.my_be.model.MasSession;
import com.example.my_be.repository.MasNegotiationRepository;
import com.example.my_be.repository.MasSessionRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MasNegotiationService {

    @Autowired
    private MasNegotiationRepository masNegotiationRepository;

    @Autowired
    private MasSessionRepository masSessionRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Lưu negotiation_result (nếu có) vào mas_negotiations.
     */
    public MasNegotiation createFromState(String sessionId, String negotiationJson) {
        if (negotiationJson == null || negotiationJson.isEmpty() || "{}".equals(negotiationJson) || "null".equalsIgnoreCase(negotiationJson)) {
            return null;
        }

        try {
            JsonNode node = objectMapper.readTree(negotiationJson);
            if (node == null || node.isMissingNode() || node.isEmpty()) {
                return null;
            }

            MasSession session = masSessionRepository.findById(sessionId)
                .orElseThrow(() -> new RuntimeException("MasSession not found: " + sessionId));

            MasNegotiation negotiation = new MasNegotiation();
            negotiation.setNegotiationId(UUID.randomUUID().toString());
            negotiation.setSession(session);

            negotiation.setInitiator(node.path("initiator").asText("planning_agent"));
            JsonNode participantsNode = node.path("participants");
            negotiation.setParticipants(participantsNode.isMissingNode() ? null : participantsNode.toString());
            negotiation.setTopic(node.path("topic").asText(null));

            JsonNode proposalsNode = node.path("proposals");
            negotiation.setProposals(proposalsNode.isMissingNode() ? null : proposalsNode.toString());
            JsonNode responsesNode = node.path("responses");
            negotiation.setResponses(responsesNode.isMissingNode() ? null : responsesNode.toString());
            JsonNode constraintsNode = node.path("constraints");
            negotiation.setConstraints(constraintsNode.isMissingNode() ? null : constraintsNode.toString());

            negotiation.setMaxRounds(node.path("max_rounds").asInt(5));
            negotiation.setCurrentRound(node.path("current_round").asInt(1));

            return masNegotiationRepository.save(negotiation);
        } catch (Exception e) {
            System.err.println("[WARN] Failed to parse negotiation_result for mas_negotiations: " + e.getMessage());
            return null;
        }
    }
}

