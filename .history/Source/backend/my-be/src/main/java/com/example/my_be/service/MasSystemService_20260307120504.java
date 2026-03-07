package com.example.my_be.service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.example.my_be.dto.MasChatRequest;
import com.example.my_be.dto.MasChatResponse;
import com.example.my_be.dto.MasSessionRequest;
import com.example.my_be.dto.MasSessionResponse;
import com.example.my_be.dto.MasStateResponse;
import com.example.my_be.model.Message;
import com.example.my_be.model.Message.MessageRole;
import com.example.my_be.model.Message.MessageStatus;
import com.example.my_be.repository.MessageRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MasSystemService {
    @Autowired
    private MasSessionService masSessionService;

    @Autowired
    private MasStateService masStateService;

    @Autowired
    private MessageRepository messageRepository;

    @Autowired
    private RestTemplate restTemplate;

    @Value("${mas.flask.api.url:http://localhost:5000}")
    private String masFlaskApiUrl;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public MasChatResponse processChat(MasChatRequest request) {
        MasSessionResponse session;
        if (request.getSessionId() == null || request.getSessionId().isEmpty()) {
            MasSessionRequest sessionRequest = new MasSessionRequest();
            sessionRequest.setUserId(request.getUserId());
            sessionRequest.setConversationId(request.getConversationId());
            session = masSessionService.createSession(sessionRequest);
        } else {
            session = masSessionService.getSessionById(request.getSessionId(), request.getUserId())
                .orElseThrow(() -> new RuntimeException("Session not found"));
        }

        Message userMessage = new Message();
        userMessage.setMessageId(UUID.randomUUID().toString());
        userMessage.setConversationId(request.getConversationId());
        userMessage.setUserId(request.getUserId());
        userMessage.setRole(MessageRole.USER);
        userMessage.setContent(request.getUserInput());
        userMessage.setStatus(MessageStatus.PENDING);
        userMessage = messageRepository.save(userMessage);

        try {
            String flaskUrl = masFlaskApiUrl + "/api/mas/chat";
            
            String requestBody = objectMapper.writeValueAsString(request);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<String> flaskResponse = restTemplate.postForEntity(flaskUrl, entity, String.class);
            
            JsonNode responseJson = objectMapper.readTree(flaskResponse.getBody());
            
            MasChatResponse response = new MasChatResponse();
            response.setSessionId(session.getSessionId());
            response.setMessageId(userMessage.getMessageId());
            response.setFinalOutput(responseJson.path("final_output").asText());
            response.setIntent(responseJson.path("intent").toString());
            response.setPlan(responseJson.path("plan").toString());
            response.setSummary(responseJson.path("summary").asText());
            response.setEvaluation(responseJson.path("evaluation").toString());
            response.setClarificationNeeded(responseJson.path("clarification_needed").asBoolean(false));
            response.setClarificationQuestion(responseJson.path("clarification_question").asText());
            response.setAgentConfidences(responseJson.path("agent_confidences").toString());
            response.setStatus("COMPLETED");

            Message assistantMessage = new Message();
            assistantMessage.setMessageId(UUID.randomUUID().toString());
            assistantMessage.setConversationId(request.getConversationId());
            assistantMessage.setUserId(request.getUserId());
            assistantMessage.setRole(MessageRole.ASSISTANT);
            assistantMessage.setContent(response.getFinalOutput());
            assistantMessage.setStatus(MessageStatus.COMPLETED);
            messageRepository.save(assistantMessage);

            userMessage.setStatus(MessageStatus.COMPLETED);
            messageRepository.save(userMessage);

            return response;
        } catch (Exception e) {
            userMessage.setStatus(MessageStatus.FAILED);
            messageRepository.save(userMessage);
            
            MasChatResponse errorResponse = new MasChatResponse();
            errorResponse.setSessionId(session.getSessionId());
            errorResponse.setMessageId(userMessage.getMessageId());
            errorResponse.setFinalOutput("Lỗi khi xử lý: " + e.getMessage());
            errorResponse.setStatus("FAILED");
            return errorResponse;
        }
    }

    public List<MasStateResponse> getSessionHistory(String sessionId, String userId) {
        masSessionService.getSessionById(sessionId, userId)
            .orElseThrow(() -> new RuntimeException("Session not found"));
        return masStateService.getStatesBySessionId(sessionId);
    }

    public Optional<MasStateResponse> getLatestState(String sessionId, String userId) {
        masSessionService.getSessionById(sessionId, userId)
            .orElseThrow(() -> new RuntimeException("Session not found"));
        return masStateService.getLatestStateBySessionId(sessionId);
    }
}
