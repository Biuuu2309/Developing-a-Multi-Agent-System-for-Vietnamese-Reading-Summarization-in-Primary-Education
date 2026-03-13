package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class CreateAgentLogRequest {
    private String sessionId;
    private String messageId;
    private String agentId;
    private String input;
    private String output;
    private Integer durationMs;
    private String status;
    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
    // Explicit setters để tránh lỗi khi IDE không xử lý được Lombok
    public void setMessageId(String messageId) {
        this.messageId = messageId;
    }

    public void setAgentId(String agentId) {
        this.agentId = agentId;
    }

    public void setInput(String input) {
        this.input = input;
    }

    public void setOutput(String output) {
        this.output = output;
    }

    public void setDurationMs(Integer durationMs) {
        this.durationMs = durationMs;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}

