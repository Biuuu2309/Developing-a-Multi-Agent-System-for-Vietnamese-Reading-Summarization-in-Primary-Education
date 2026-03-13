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

import com.example.my_be.dto.CreateAgentLogRequest;
import com.example.my_be.dto.MasChatRequest;
import com.example.my_be.dto.MasChatResponse;
import com.example.my_be.dto.MasSessionRequest;
import com.example.my_be.dto.MasSessionResponse;
import com.example.my_be.dto.MasStateResponse;
import com.example.my_be.model.Agent;
import com.example.my_be.model.Agent.AgentType;
import com.example.my_be.model.Message;
import com.example.my_be.model.Message.MessageRole;
import com.example.my_be.model.Message.MessageStatus;
import com.example.my_be.repository.MessageRepository;
import com.example.my_be.service.AgentService;
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
    private AgentLogService agentLogService;

    @Autowired
    private AgentService agentService;

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

        Message userMessage = new Message(
                UUID.randomUUID().toString(),
                request.getConversationId(),
                request.getUserId(),
                null,
                MessageRole.USER,
                request.getUserInput(),
                null,
                MessageStatus.PENDING,
                null
        );
        userMessage = messageRepository.save(userMessage);

        try {
            String flaskUrl = masFlaskApiUrl + "/api/mas/chat";
            
            String requestBody = objectMapper.writeValueAsString(request);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<String> flaskResponse = restTemplate.postForEntity(flaskUrl, entity, String.class);
            
            // Debug: Log Flask response
            System.out.println("[DEBUG] Flask response status: " + flaskResponse.getStatusCode());
            System.out.println("[DEBUG] Flask response body: " + flaskResponse.getBody());
            
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

            // Ghi AgentLog cơ bản dựa trên thông tin MAS trả về
            // Flask trả về agent_confidences là JSON string, cần parse lại thành JsonNode object
            JsonNode agentConfs = null;
            try {
                JsonNode agentConfsRaw = responseJson.path("agent_confidences");
                if (!agentConfsRaw.isMissingNode() && agentConfsRaw.isTextual()) {
                    // Parse từ JSON string thành object
                    agentConfs = objectMapper.readTree(agentConfsRaw.asText());
                } else if (agentConfsRaw.isObject()) {
                    // Nếu đã là object thì dùng trực tiếp
                    agentConfs = agentConfsRaw;
                }
            } catch (Exception e) {
                System.err.println("Error parsing agent_confidences: " + e.getMessage());
            }

            // Helper log cho từng agent nếu có confidence
            // planning_agent -> PLANNING
            logAgentIfPresent(agentConfs,
                    session.getSessionId(),
                    "planning_agent",                    // key trong JSON agent_confidences
                    AgentType.PLANNING,                  // agent_type trong DB
                    userMessage.getMessageId(),
                    request.getUserInput(),
                    responseJson.path("plan").toString());

            // abstractive_agent -> ABSTRACTER
            logAgentIfPresent(agentConfs,
                    session.getSessionId(),
                    "abstractive_agent",
                    AgentType.ABSTRACTER,
                    userMessage.getMessageId(),
                    responseJson.path("summary").asText(),
                    response.getFinalOutput());

            // evaluation_agent -> EVALUATION
            logAgentIfPresent(agentConfs,
                    session.getSessionId(),
                    "evaluation_agent",
                    AgentType.EVALUATION,
                    userMessage.getMessageId(),
                    responseJson.path("summary").asText(),
                    responseJson.path("evaluation").toString());
            
            Message assistantMessage = new Message(
                    UUID.randomUUID().toString(),
                    request.getConversationId(),
                    request.getUserId(),
                    null,
                    MessageRole.ASSISTANT,
                    response.getFinalOutput(),
                    null,
                    MessageStatus.COMPLETED,
                    null
            );
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

    private void logAgentIfPresent(JsonNode agentConfs,
                                   String sessionId,
                                   String confidenceKey,
                                   String agentId,
                                   String messageId,
                                   String input,
                                   String output) {
        try {
            if (agentConfs != null && agentConfs.has(confidenceKey)) {
                System.out.println("[DEBUG] Logging agent: " + confidenceKey + " (agentId: " + agentId + ")");
                CreateAgentLogRequest logReq = new CreateAgentLogRequest();
                logReq.setSessionId(sessionId);
                logReq.setMessageId(messageId);
                logReq.setAgentId(agentId);
                logReq.setInput(input);
                logReq.setOutput(output);
                logReq.setDurationMs(null);
                logReq.setStatus("SUCCESS");
                agentLogService.createAgentLog(logReq);
                System.out.println("[DEBUG] Agent log created successfully for: " + confidenceKey);
            } else {
                System.out.println("[DEBUG] Agent " + confidenceKey + " not found in agent_confidences. agentConfs is null: " + (agentConfs == null));
            }
        } catch (Exception e) {
            System.err.println("[ERROR] Failed to log agent " + confidenceKey + ": " + e.getMessage());
            e.printStackTrace();
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
