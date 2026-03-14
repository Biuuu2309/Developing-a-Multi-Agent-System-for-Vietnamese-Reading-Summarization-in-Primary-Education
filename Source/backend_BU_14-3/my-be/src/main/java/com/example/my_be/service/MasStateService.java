package com.example.my_be.service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.dto.MasStateRequest;
import com.example.my_be.dto.MasStateResponse;
import com.example.my_be.model.MasSession;
import com.example.my_be.model.MasState;
import com.example.my_be.model.Message;
import com.example.my_be.repository.MasSessionRepository;
import com.example.my_be.repository.MasStateRepository;
import com.example.my_be.repository.MessageRepository;

@Service
public class MasStateService {
    @Autowired
    private MasStateRepository masStateRepository;

    @Autowired
    private MasSessionRepository masSessionRepository;

    @Autowired
    private MessageRepository messageRepository;

    public MasStateResponse createState(MasStateRequest request) {
        MasSession session = masSessionRepository.findById(request.getSessionId())
            .orElseThrow(() -> new RuntimeException("Session not found"));

        MasState state = new MasState();
        state.setStateId(UUID.randomUUID().toString());
        state.setSession(session);
        state.setUserInput(request.getUserInput());
        state.setHistory(request.getHistory());
        state.setIntent(request.getIntent());
        state.setClarificationNeeded(request.getClarificationNeeded());
        state.setClarificationQuestion(request.getClarificationQuestion());
        state.setPlan(request.getPlan());
        state.setOriginalText(request.getOriginalText());
        state.setSummary(request.getSummary());
        state.setEvaluation(request.getEvaluation());
        state.setFinalOutput(request.getFinalOutput());
        state.setPlanRevisionCount(request.getPlanRevisionCount());
        state.setStrategyChanged(request.getStrategyChanged());
        state.setImprovementCount(request.getImprovementCount());
        state.setNeedsImprovement(request.getNeedsImprovement());
        state.setImagePath(request.getImagePath());
        state.setExtractedText(request.getExtractedText());
        state.setGoalState(request.getGoalState());
        state.setAgentConfidences(request.getAgentConfidences());
        state.setNegotiationResult(request.getNegotiationResult());
        state.setAgentMemories(request.getAgentMemories());
        state.setSemanticRecall(request.getSemanticRecall());
        state.setToolRecommendations(request.getToolRecommendations());
        state.setKnowledgeSearch(request.getKnowledgeSearch());

        if (request.getMessageId() != null) {
            Message message = messageRepository.findById(request.getMessageId()).orElse(null);
            state.setMessage(message);
        }

        MasState saved = masStateRepository.save(state);
        return toResponse(saved);
    }

    public List<MasStateResponse> getStatesBySessionId(String sessionId) {
        return masStateRepository.findBySessionSessionId(sessionId)
            .stream()
            .map(this::toResponse)
            .collect(Collectors.toList());
    }

    public Optional<MasStateResponse> getLatestStateBySessionId(String sessionId) {
        return masStateRepository.findFirstBySessionSessionIdOrderByCreatedAtDesc(sessionId)
            .map(this::toResponse);
    }

    public Optional<MasStateResponse> getStateById(String stateId, String sessionId) {
        return masStateRepository.findByStateIdAndSessionSessionId(stateId, sessionId)
            .map(this::toResponse);
    }

    public MasStateResponse updateState(String stateId, MasStateRequest request) {
        MasState state = masStateRepository.findById(stateId)
            .orElseThrow(() -> new RuntimeException("State not found"));

        if (request.getUserInput() != null) state.setUserInput(request.getUserInput());
        if (request.getHistory() != null) state.setHistory(request.getHistory());
        if (request.getIntent() != null) state.setIntent(request.getIntent());
        if (request.getClarificationNeeded() != null) state.setClarificationNeeded(request.getClarificationNeeded());
        if (request.getClarificationQuestion() != null) state.setClarificationQuestion(request.getClarificationQuestion());
        if (request.getPlan() != null) state.setPlan(request.getPlan());
        if (request.getOriginalText() != null) state.setOriginalText(request.getOriginalText());
        if (request.getSummary() != null) state.setSummary(request.getSummary());
        if (request.getEvaluation() != null) state.setEvaluation(request.getEvaluation());
        if (request.getFinalOutput() != null) state.setFinalOutput(request.getFinalOutput());
        if (request.getPlanRevisionCount() != null) state.setPlanRevisionCount(request.getPlanRevisionCount());
        if (request.getStrategyChanged() != null) state.setStrategyChanged(request.getStrategyChanged());
        if (request.getImprovementCount() != null) state.setImprovementCount(request.getImprovementCount());
        if (request.getNeedsImprovement() != null) state.setNeedsImprovement(request.getNeedsImprovement());
        if (request.getImagePath() != null) state.setImagePath(request.getImagePath());
        if (request.getExtractedText() != null) state.setExtractedText(request.getExtractedText());
        if (request.getGoalState() != null) state.setGoalState(request.getGoalState());
        if (request.getAgentConfidences() != null) state.setAgentConfidences(request.getAgentConfidences());
        if (request.getNegotiationResult() != null) state.setNegotiationResult(request.getNegotiationResult());
        if (request.getAgentMemories() != null) state.setAgentMemories(request.getAgentMemories());
        if (request.getSemanticRecall() != null) state.setSemanticRecall(request.getSemanticRecall());
        if (request.getToolRecommendations() != null) state.setToolRecommendations(request.getToolRecommendations());
        if (request.getKnowledgeSearch() != null) state.setKnowledgeSearch(request.getKnowledgeSearch());

        MasState updated = masStateRepository.save(state);
        return toResponse(updated);
    }

    private MasStateResponse toResponse(MasState state) {
        MasStateResponse response = new MasStateResponse();
        response.setStateId(state.getStateId());
        response.setSessionId(state.getSession().getSessionId());
        response.setMessageId(state.getMessage() != null ? state.getMessage().getMessageId() : null);
        response.setUserInput(state.getUserInput());
        response.setHistory(state.getHistory());
        response.setIntent(state.getIntent());
        response.setClarificationNeeded(state.getClarificationNeeded());
        response.setClarificationQuestion(state.getClarificationQuestion());
        response.setPlan(state.getPlan());
        response.setOriginalText(state.getOriginalText());
        response.setSummary(state.getSummary());
        response.setEvaluation(state.getEvaluation());
        response.setFinalOutput(state.getFinalOutput());
        response.setPlanRevisionCount(state.getPlanRevisionCount());
        response.setStrategyChanged(state.getStrategyChanged());
        response.setImprovementCount(state.getImprovementCount());
        response.setNeedsImprovement(state.getNeedsImprovement());
        response.setImagePath(state.getImagePath());
        response.setExtractedText(state.getExtractedText());
        response.setGoalState(state.getGoalState());
        response.setAgentConfidences(state.getAgentConfidences());
        response.setNegotiationResult(state.getNegotiationResult());
        response.setAgentMemories(state.getAgentMemories());
        response.setSemanticRecall(state.getSemanticRecall());
        response.setToolRecommendations(state.getToolRecommendations());
        response.setKnowledgeSearch(state.getKnowledgeSearch());
        response.setCreatedAt(state.getCreatedAt());
        response.setUpdatedAt(state.getUpdatedAt());
        return response;
    }
}
