package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MasStateRequest {
    private String sessionId;
    private String messageId;
    private String userInput;
    private String history;
    private String intent;
    private Boolean clarificationNeeded;
    private String clarificationQuestion;
    private String plan;
    private String originalText;
    private String summary;
    private String evaluation;
    private String finalOutput;
    private Integer planRevisionCount;
    private Boolean strategyChanged;
    private Integer improvementCount;
    private Boolean needsImprovement;
    private String imagePath;
    private String extractedText;
    private String goalState;
    private String agentConfidences;
    private String negotiationResult;
    private String agentMemories;
}
