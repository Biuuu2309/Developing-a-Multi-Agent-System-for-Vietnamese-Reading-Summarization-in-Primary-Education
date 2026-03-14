package com.example.my_be.service;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.regex.Pattern;

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
import com.example.my_be.dto.MasStateRequest;
import com.example.my_be.dto.MasStateResponse;
import com.example.my_be.model.Agent;
import com.example.my_be.model.Agent.AgentType;
import com.example.my_be.model.Message;
import com.example.my_be.model.Message.MessageRole;
import com.example.my_be.model.Message.MessageStatus;
import com.example.my_be.repository.MessageRepository;
import com.example.my_be.service.AgentService;
import com.example.my_be.service.SummaryService;
import com.example.my_be.service.UserService;
import com.example.my_be.model.Summary;
import com.example.my_be.model.User;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MasSystemService {
    @Autowired
    private MasSessionService masSessionService;

    @Autowired
    private MasStateService masStateService;

    @Autowired
    private MasPlanService masPlanService;

    @Autowired
    private MasEvaluationService masEvaluationService;

    @Autowired
    private MasGoalService masGoalService;

    @Autowired
    private MasNegotiationService masNegotiationService;

    @Autowired
    private MasAgentConfidenceService masAgentConfidenceService;

    @Autowired
    private MasAgentMemoryService masAgentMemoryService;

    @Autowired
    private MessageRepository messageRepository;

    @Autowired
    private AgentLogService agentLogService;

    @Autowired
    private AgentService agentService;

    @Autowired
    private SummaryService summaryService;

    @Autowired
    private UserService userService;

    @Autowired
    private SummarySessionService summarySessionService;

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
            boolean clarificationNeeded = responseJson.path("clarification_needed").asBoolean(false);
            response.setClarificationNeeded(clarificationNeeded);
            response.setClarificationQuestion(responseJson.path("clarification_question").asText());
            response.setAgentConfidences(responseJson.path("agent_confidences").toString());
            response.setStatus("COMPLETED");

            // Parse agent_confidences từ Flask (dùng cho nhiều nơi)
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

            // Lưu MAS state snapshot vào mas_states
            MasStateRequest stateRequest = new MasStateRequest();
            stateRequest.setSessionId(session.getSessionId());
            stateRequest.setMessageId(userMessage.getMessageId());
            stateRequest.setUserInput(request.getUserInput());
            // Hiện tại chưa lấy history từ Flask riêng, có thể bổ sung sau
            stateRequest.setHistory(null);
            stateRequest.setIntent(responseJson.path("intent").asText());
            stateRequest.setClarificationNeeded(responseJson.path("clarification_needed").asBoolean(false));
            stateRequest.setClarificationQuestion(responseJson.path("clarification_question").asText());
            stateRequest.setPlan(responseJson.path("plan").asText());
            stateRequest.setOriginalText(responseJson.path("original_text").asText());
            stateRequest.setSummary(responseJson.path("summary").asText());
            stateRequest.setEvaluation(responseJson.path("evaluation").asText());
            stateRequest.setFinalOutput(responseJson.path("final_output").asText());
            // Các field nâng cao: để null / mặc định, sẽ dùng khi có self-improvement loop
            stateRequest.setPlanRevisionCount(null);
            stateRequest.setStrategyChanged(null);
            stateRequest.setImprovementCount(null);
            stateRequest.setNeedsImprovement(null);
            // Image OCR fields: hiện Flask chưa trả, để null
            stateRequest.setImagePath(null);
            stateRequest.setExtractedText(null);
            // Advanced MAS fields từ Flask
            stateRequest.setGoalState(responseJson.path("goal_state").asText());
            stateRequest.setAgentConfidences(responseJson.path("agent_confidences").asText());
            stateRequest.setNegotiationResult(responseJson.path("negotiation_result").asText());
            stateRequest.setAgentMemories(responseJson.path("agent_memories").asText());
            // Advanced Memory: semantic recall, tool recommendations, knowledge search
            stateRequest.setSemanticRecall(responseJson.path("semantic_recall").asText());
            stateRequest.setToolRecommendations(responseJson.path("tool_recommendations").asText());
            stateRequest.setKnowledgeSearch(responseJson.path("knowledge_search").asText());

            MasStateResponse savedState = masStateService.createState(stateRequest);

            // Lưu plan chi tiết vào mas_plans
            masPlanService.createFromState(
                savedState.getStateId(),
                stateRequest.getIntent(),
                stateRequest.getPlan()
            );

            // Lưu evaluation chi tiết vào mas_evaluations
            masEvaluationService.createFromState(
                savedState.getStateId(),
                stateRequest.getEvaluation()
            );

            // Lưu goal_state (nếu có) vào mas_goals
            masGoalService.createFromState(
                session.getSessionId(),
                stateRequest.getGoalState()
            );

            // Lưu negotiation_result (nếu có) vào mas_negotiations
            masNegotiationService.createFromState(
                session.getSessionId(),
                stateRequest.getNegotiationResult()
            );

            // Lưu agent_confidences vào mas_agent_confidences
            masAgentConfidenceService.createFromState(
                session.getSessionId(),
                agentConfs,
                "summarization"
            );

            // Lưu agent_memories (nếu serialize được) vào mas_agent_memories
            masAgentMemoryService.createFromState(
                stateRequest.getAgentMemories(),
                "summarization"
            );

            // Tạo bản ghi summaries cho người dùng nếu đã có summary cuối cùng (không cần clarification)
            if (!clarificationNeeded) {
                createSummaryFromMas(request, responseJson);
            }

            // Ghi AgentLog cơ bản dựa trên thông tin MAS trả về
            // Helper log cho từng agent nếu có confidence
            // planning_agent -> PLANNING
            logAgentIfPresent(agentConfs,
                    session.getSessionId(),
                    "planning_agent",                    // key trong JSON agent_confidences
                    AgentType.PLANNING,                  // agent_type trong DB
                    userMessage.getMessageId(),
                    request.getUserInput(),
                    responseJson.path("plan").toString());

            // evaluation_agent -> EVALUATION
            logAgentIfPresent(agentConfs,
                    session.getSessionId(),
                    "evaluation_agent",
                    AgentType.EVALUATION,
                    userMessage.getMessageId(),
                    responseJson.path("summary").asText(),
                    responseJson.path("evaluation").toString());

            // Chọn agent tóm tắt theo summarization_type trong intent
            try {
                String intentRaw = responseJson.path("intent").asText(); // JSON string
                String summaryType = null;

                if (intentRaw != null && !intentRaw.isEmpty()) {
                    JsonNode intentNode = objectMapper.readTree(intentRaw); // parse JSON bên trong
                    summaryType = intentNode.path("summarization_type").asText(null);
                }

                if ("abstractive".equalsIgnoreCase(summaryType)) {
                    // abstractive -> abstractive_agent / ABSTRACTER
                    logAgentIfPresent(agentConfs,
                            session.getSessionId(),
                            "abstractive_agent",          // key trong agent_confidences từ Flask
                            AgentType.ABSTRACTER,
                            userMessage.getMessageId(),
                            responseJson.path("summary").asText(),
                            response.getFinalOutput());
                } else if ("extractive".equalsIgnoreCase(summaryType)) {
                    // extractive -> extractive_agent / EXTRACTOR
                    // Lưu ý: bên MAS_main.py dùng key \"extractive_agent\" (không phải \"extractor_agent\")
                    logAgentIfPresent(agentConfs,
                            session.getSessionId(),
                            "extractive_agent",
                            AgentType.EXTRACTOR,
                            userMessage.getMessageId(),
                            responseJson.path("summary").asText(),
                            response.getFinalOutput());
                } else {
                    System.out.println("[DEBUG] summarization_type is null/unknown: " + summaryType + " -> skip summary agent log");
                }
            } catch (Exception e) {
                System.err.println("[ERROR] Failed to parse intent for summarization_type: " + e.getMessage());
            }
            
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

    private void createSummaryFromMas(MasChatRequest request, JsonNode responseJson) {
        try {
            // Lấy user tạo summary
            String userId = request.getUserId();
            if (userId == null || userId.isEmpty()) {
                return;
            }
            User user = userService.getUserById(userId).orElse(null);
            if (user == null) {
                return;
            }

            // Lấy original_text (nếu có), fallback userInput
            String originalText = responseJson.path("original_text").asText();
            if (originalText == null || originalText.isBlank()) {
                originalText = request.getUserInput();
            }

            String summaryText = responseJson.path("summary").asText();
            if (summaryText == null || summaryText.isBlank()) {
                return; // Không có summary thì không tạo bản ghi
            }

            // Parse intent để lấy grade_level và summarization_type
            String intentRaw = responseJson.path("intent").asText();
            String grade = null;
            String method = null;
            try {
                if (intentRaw != null && !intentRaw.isEmpty()) {
                    JsonNode intentNode = objectMapper.readTree(intentRaw);
                    int gradeLevel = intentNode.path("grade_level").asInt(0);
                    if (gradeLevel > 0) {
                        grade = String.valueOf(gradeLevel);
                    }
                    String summarizationType = intentNode.path("summarization_type").asText("abstractive");
                    if ("extractive".equalsIgnoreCase(summarizationType)) {
                        method = "extractive";          // Extractive (PhoBERTSUM)
                    } else {
                        method = "abstractive";     // Abstractive (ViT5 diễn giải)
                    }
                }
            } catch (Exception e) {
                System.err.println("[WARN] Failed to parse intent for summary mapping: " + e.getMessage());
            }

            if (method == null) {
                method = "abstractive";
            }

            // Tạo title: Lấy 6 chữ đầu của văn bản gốc ...
            String preview = originalText != null ? originalText.trim() : "";
            String[] words = preview.split("\\s+");
            StringBuilder firstWords = new StringBuilder();
            int maxWords = Math.min(6, words.length);
            for (int i = 0; i < maxWords; i++) {
                if (i > 0) firstWords.append(" ");
                firstWords.append(words[i]);
            }
            String titleCore = firstWords.toString().trim();
            if (titleCore.isEmpty()) {
                titleCore = "Không có tiêu đề";
            }
            String title = titleCore + "...";

            Summary summary = new Summary();
            summary.setTitle(title);
            summary.setContent(originalText);
            summary.setSummaryContent(summaryText);
            summary.setCreatedBy(user);
            summary.setMethod(method);
            summary.setGrade(grade);
            summary.setStatus("APPROVED"); // Cho phép hiển thị ngay trong danh sách
            // Đồng bộ với logic createSummary trong SummaryController
            if (summary.getCreatedAt() == null) {
                summary.setCreatedAt(new java.util.Date());
            }
            if ("APPROVED".equals(summary.getStatus())) {
                summary.setApprovedAt(new java.util.Date());
            }

            Summary savedSummary = summaryService.createSummary(summary);
            
            // Tự động tạo hình ảnh từ summary content
            generateImagesForSummary(savedSummary, summaryText);
        } catch (Exception e) {
            System.err.println("[WARN] Failed to create summary from MAS result: " + e.getMessage());
        }
    }

    /**
     * Đếm số câu trong văn bản tiếng Việt
     */
    private int countSentences(String text) {
        if (text == null || text.trim().isEmpty()) {
            return 0;
        }
        
        String trimmed = text.trim();
        // Pattern để tách câu: kết thúc bằng . ! ? và có khoảng trắng sau, hoặc ở cuối text
        Pattern sentencePattern = Pattern.compile("[.!?]+(\\s+|$)");
        String[] parts = sentencePattern.split(trimmed);
        
        // Đếm số dấu câu trong text
        int punctuationCount = 0;
        for (int i = 0; i < trimmed.length(); i++) {
            char c = trimmed.charAt(i);
            if (c == '.' || c == '!' || c == '?') {
                punctuationCount++;
            }
        }
        
        // Nếu không có dấu câu, coi như 1 câu
        if (punctuationCount == 0) {
            return 1;
        }
        
        // Số câu = số dấu câu (mỗi dấu câu kết thúc 1 câu)
        // Nhưng cần xử lý trường hợp nhiều dấu câu liên tiếp (ví dụ: "...")
        int sentenceCount = 0;
        boolean inPunctuation = false;
        for (int i = 0; i < trimmed.length(); i++) {
            char c = trimmed.charAt(i);
            if (c == '.' || c == '!' || c == '?') {
                if (!inPunctuation) {
                    sentenceCount++;
                    inPunctuation = true;
                }
            } else if (c != ' ') {
                inPunctuation = false;
            }
        }
        
        return Math.max(1, sentenceCount);
    }

    /**
     * Tính số lượng hình ảnh cần tạo dựa trên số câu
     * - < 4 câu: 1 hình
     * - 4-7 câu: 2 hình
     * - 8-11 câu: 3 hình
     * - >= 12 câu: số câu / 4 (chia lấy nguyên)
     */
    private int calculateImageCount(int sentenceCount) {
        if (sentenceCount < 4) {
            return 1;
        } else if (sentenceCount < 8) {
            return 2;
        } else if (sentenceCount < 12) {
            return 3;
        } else {
            return sentenceCount / 4;
        }
    }

    /**
     * Chia summary thành các phần để tạo hình ảnh
     */
    private List<String> splitSummaryIntoParts(String summaryText, int imageCount) {
        List<String> parts = new ArrayList<>();
        if (summaryText == null || summaryText.trim().isEmpty() || imageCount <= 0) {
            return parts;
        }

        // Tách thành câu
        Pattern sentencePattern = Pattern.compile("[.!?]+\\s+");
        String[] sentences = sentencePattern.split(summaryText.trim());
        
        // Nếu chỉ có 1 câu hoặc 1 hình, trả về toàn bộ
        if (sentences.length <= 1 || imageCount == 1) {
            parts.add(summaryText.trim());
            return parts;
        }

        // Chia đều các câu vào các phần
        int sentencesPerPart = (int) Math.ceil((double) sentences.length / imageCount);
        
        for (int i = 0; i < imageCount; i++) {
            int startIdx = i * sentencesPerPart;
            int endIdx = Math.min(startIdx + sentencesPerPart, sentences.length);
            
            if (startIdx < sentences.length) {
                StringBuilder part = new StringBuilder();
                for (int j = startIdx; j < endIdx; j++) {
                    if (j > startIdx) {
                        part.append(" ");
                    }
                    part.append(sentences[j].trim());
                    // Thêm dấu câu nếu câu không kết thúc bằng dấu câu
                    if (!sentences[j].trim().matches(".*[.!?]$")) {
                        part.append(".");
                    }
                }
                String partText = part.toString().trim();
                if (!partText.isEmpty()) {
                    parts.add(partText);
                }
            }
        }

        return parts;
    }

    /**
     * Tạo và upload hình ảnh cho summary
     */
    private void generateImagesForSummary(Summary summary, String summaryText) {
        try {
            int sentenceCount = countSentences(summaryText);
            int imageCount = calculateImageCount(sentenceCount);
            
            System.out.println("[DEBUG] Summary has " + sentenceCount + " sentences, will generate " + imageCount + " images");
            
            if (imageCount <= 0) {
                return;
            }

            List<String> parts = splitSummaryIntoParts(summaryText, imageCount);
            List<String> imageUrls = new ArrayList<>();

            for (int i = 0; i < parts.size(); i++) {
                String part = parts.get(i);
                try {
                    System.out.println("[DEBUG] Generating image " + (i + 1) + "/" + parts.size() + " for part: " + part.substring(0, Math.min(50, part.length())) + "...");
                    SummarySessionService.ImageUploadResult result = summarySessionService.generateImageAndUploadToCloudinary(part);
                    
                    if (result.isSuccess() && result.getImageUrl() != null) {
                        imageUrls.add(result.getImageUrl());
                        System.out.println("[DEBUG] Image " + (i + 1) + " uploaded successfully: " + result.getImageUrl());
                    } else {
                        System.err.println("[WARN] Failed to generate image " + (i + 1));
                    }
                } catch (Exception e) {
                    System.err.println("[ERROR] Error generating image " + (i + 1) + ": " + e.getMessage());
                    e.printStackTrace();
                }
            }

            // Lưu image URLs dưới dạng JSON array string
            if (!imageUrls.isEmpty()) {
                String imageUrlsJson = objectMapper.writeValueAsString(imageUrls);
                summary.setImageUrl(imageUrlsJson);
                summaryService.updateSummary(summary);
                System.out.println("[DEBUG] Saved " + imageUrls.size() + " image URLs to summary");
            } else {
                System.err.println("[WARN] No images were generated successfully");
            }
        } catch (Exception e) {
            System.err.println("[ERROR] Failed to generate images for summary: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void logAgentIfPresent(JsonNode agentConfs,
                                   String sessionId,
                                   String confidenceKey,
                                   AgentType agentType,
                                   String messageId,
                                   String input,
                                   String output) {
        try {
            if (agentConfs != null && agentConfs.has(confidenceKey)) {
                // Query agent từ database theo agent_type
                Agent agent = agentService.getAgentByType(agentType)
                    .orElse(null);
                
                if (agent == null) {
                    System.err.println("[WARN] Agent with type " + agentType + " not found in database. Skipping log.");
                    return;
                }
                
                System.out.println("[DEBUG] Logging agent: " + confidenceKey + " (agentId: " + agent.getAgentId() + ", agentType: " + agentType + ")");
                CreateAgentLogRequest logReq = new CreateAgentLogRequest();
                logReq.setSessionId(sessionId);
                logReq.setMessageId(messageId);
                logReq.setAgentId(agent.getAgentId());
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
