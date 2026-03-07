package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MasChatResponse {
    private String sessionId;
    private String stateId;
    private String messageId;
    private String finalOutput;
    private String intent;
    private String plan;
    private String summary;
    private String evaluation;
    private Boolean clarificationNeeded;
    private String clarificationQuestion;
    private String agentConfidences;
    private String status;
}
