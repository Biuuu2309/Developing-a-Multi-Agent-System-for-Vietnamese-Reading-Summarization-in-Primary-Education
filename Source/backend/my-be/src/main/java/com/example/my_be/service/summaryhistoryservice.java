package com.example.my_be.service;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import com.example.my_be.dto.SummaryHistoryDTO;
import com.example.my_be.model.SummaryHistory;
import com.example.my_be.model.SummarySession;
import com.example.my_be.repository.SummaryHistoryRepository;
import com.example.my_be.repository.SummarySessionRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

@Service
public class SummaryHistoryService {

    @Autowired
    private SummaryHistoryRepository summaryHistoryRepository;

    @Autowired
    private SummarySessionRepository summarySessionRepository;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private ObjectMapper objectMapper; // Inject ObjectMapper

    public SummaryHistoryDTO createSummaryHistory(SummarySession session, String method, String content) {
        return createSummaryHistory(session, method, content, null);
    }

    @Transactional
    public SummaryHistoryDTO createSummaryHistory(SummarySession session, String method, String content, Integer grade) {
        try {
            SummaryHistory history = new SummaryHistory();
            history.setSession(session);
            history.setMethod(method);

            if (method.equals("paraphrase") || method.equals("abstractive")) {
                // For testing, return a mock summary instead of calling external API
                history.setSummaryContent("Đây là nội dung diễn giải cho: " + content.substring(0, Math.min(50, content.length())) + "...");
            } else if (method.equals("extraction") || method.equals("extract") || method.equals("extractive")) {
                // For testing, return a mock summary instead of calling external API
                history.setSummaryContent("Đây là nội dung trích xuất cho: " + content.substring(0, Math.min(50, content.length())) + "...");
            } else {
                history.setSummaryContent("Phương thức không được hỗ trợ: " + method);
            }

            history.setAccepted(false);

            System.out.println("Saving summaryContent: " + history.getSummaryContent());
            System.out.println("History: " + history);
            System.out.println("Historyid: " + history.getHistoryId());
            SummaryHistory savedHistory = summaryHistoryRepository.save(history);
            return mapToDTO(savedHistory);
        } catch (Exception e) {
            System.err.println("Error creating summary history: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("Failed to create summary history: " + e.getMessage());
        }
    }

    private String callParaphraseApi(String text, Integer grade) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
    
            String url = "http://localhost:5001/summarize";
            ObjectNode payload = objectMapper.createObjectNode();
            payload.put("text", text);
            if (grade != null) {
                payload.put("grade", grade);
            }
            payload.put("max_tokens", 512);
            String json = objectMapper.writeValueAsString(payload);
            System.out.println("Paraphrase API payload: " + json);
    
            HttpEntity<String> entity = new HttpEntity<>(json, headers);
    
            ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
            System.out.println("Paraphrase API raw response: " + response.getBody());
    
            if (response.getStatusCode().is2xxSuccessful()) {
                JsonNode jsonNode = objectMapper.readTree(response.getBody());
                JsonNode summaryNode = jsonNode.get("summary");
                if (summaryNode != null && !summaryNode.isNull()) {
                    String summaryText = summaryNode.asText();
                    System.out.println("Paraphrase API response: " + summaryText);
                    return summaryText;
                }
                System.err.println("Paraphrase API returned no summary field: " + response.getBody());
                return "Không thể diễn giải nội dung (API không trả về summary)";
            } else {
                System.err.println("Failed to paraphrase text, API returned: " + response.getStatusCode());
                return "Không thể diễn giải nội dung (API lỗi: " + response.getStatusCode() + ")";
            }
        } catch (Exception e) {
            System.err.println("Error calling paraphrase API: " + e.getMessage());
            e.printStackTrace();
            return "Không thể diễn giải nội dung (Lỗi: " + e.getMessage() + ")";
        }
    }
    private String callExtractionApi(String text, Integer grade) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            String url = "http://localhost:8000/summarize";
            // Build JSON payload using ObjectMapper
            ObjectNode payload = objectMapper.createObjectNode();
            payload.put("text", text);
            if (grade != null) {
                payload.put("grade", grade);
            }
            String json = objectMapper.writeValueAsString(payload);
            System.out.println("Extraction API payload: " + json);

            HttpEntity<String> entity = new HttpEntity<>(json, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
            if (response.getStatusCode().is2xxSuccessful()) {
                JsonNode jsonNode = objectMapper.readTree(response.getBody());
                JsonNode summaryNode = jsonNode.get("summary");
                if (summaryNode != null && !summaryNode.isNull()) {
                    System.out.println("Extraction API response: " + summaryNode.asText());
                    return summaryNode.asText();
                } else {
                    System.err.println("Extraction API returned no summary field: " + response.getBody());
                    return "Không thể trích xuất nội dung (API không trả về summary)";
                }
            } else {
                System.err.println("Failed to extract text, API returned: " + response.getStatusCode());
                return "Không thể trích xuất nội dung (API lỗi: " + response.getStatusCode() + ")";
            }
        } catch (Exception e) {
            System.err.println("Error calling extraction API: " + e.getMessage());
            e.printStackTrace();
            return "Không thể trích xuất nội dung (Lỗi: " + e.getMessage() + ")";
        }
    }

    public Optional<SummaryHistoryDTO> getSummaryHistoryById(Long historyId) {
        Optional<SummaryHistory> historyOpt = summaryHistoryRepository.findById(historyId);
        return historyOpt.map(this::mapToDTO);
    }

    public SummaryHistoryDTO updateSummaryHistory(SummaryHistoryDTO historyDTO) {
        Optional<SummaryHistory> existingOpt = summaryHistoryRepository.findById(historyDTO.getHistoryId());
        if (existingOpt.isEmpty()) {
            return null;
        }

        SummaryHistory existing = existingOpt.get();
        existing.setMethod(historyDTO.getMethod());
        existing.setSummaryContent(historyDTO.getSummaryContent());
        existing.setAccepted(historyDTO.getIsAccepted());

        SummaryHistory updatedHistory = summaryHistoryRepository.save(existing);
        return mapToDTO(updatedHistory);
    }

    public void deleteSummaryHistory(Long historyId) {
        summaryHistoryRepository.deleteById(historyId);
    }

    public List<SummaryHistory> findBySession(SummarySession session) {
        return summaryHistoryRepository.findBySession(session);
    }

    @Transactional
    public SummaryHistoryDTO createSummaryHistoryFromMas(Long summarySessionId, String userInput,
            String summaryContent, String summaryImageUrl, String evaluation, String masSessionId, String conversationId) {
        SummarySession session = summarySessionRepository.findById(summarySessionId)
                .orElseThrow(() -> new RuntimeException("Summary session not found"));
        SummaryHistory history = new SummaryHistory();
        history.setSession(session);
        history.setMethod("MAS_CHAT");
        history.setSummaryContent(summaryContent != null ? summaryContent : "");
        history.setAccepted(false);
        history.setUserInput(userInput);
        history.setSummaryImageUrl(summaryImageUrl);
        history.setEvaluation(evaluation);
        history.setMasSessionId(masSessionId);
        history.setConversationId(conversationId);
        SummaryHistory saved = summaryHistoryRepository.save(history);
        return mapToDTO(saved);
    }

    public SummaryHistoryDTO mapToDTO(SummaryHistory history) {
        SummaryHistoryDTO dto = new SummaryHistoryDTO();
        dto.setHistoryId(history.getHistoryId());
        dto.setMethod(history.getMethod());
        dto.setSummaryContent(history.getSummaryContent());
        dto.setIsAccepted(history.isAccepted());
        dto.setUserInput(history.getUserInput());
        dto.setSummaryImageUrl(history.getSummaryImageUrl());
        dto.setEvaluation(history.getEvaluation());
        dto.setMasSessionId(history.getMasSessionId());
        dto.setConversationId(history.getConversationId());
        if (history.getSession() != null) {
            dto.setSessionId(history.getSession().getSessionId());
            dto.setTimestamp(history.getSession().getTimestamp());
        }
        return dto;
    }

    private SummaryHistory mapToEntity(SummaryHistoryDTO historyDTO) {
        SummaryHistory history = new SummaryHistory();
        history.setHistoryId(historyDTO.getHistoryId());
        history.setMethod(historyDTO.getMethod());
        history.setSummaryContent(historyDTO.getSummaryContent());
        history.setAccepted(historyDTO.getIsAccepted());
        // Important: keep the relation to SummarySession.
        // If we don't set session, JPA will save with session_id = null, so the row
        // disappears from "histories by sessionId" queries after update.
        if (historyDTO.getSessionId() != null) {
            Optional<SummarySession> sessionOpt = summarySessionRepository.findById(historyDTO.getSessionId());
            if (sessionOpt.isPresent()) {
                history.setSession(sessionOpt.get());
            }
        }
        return history;
    }
}
