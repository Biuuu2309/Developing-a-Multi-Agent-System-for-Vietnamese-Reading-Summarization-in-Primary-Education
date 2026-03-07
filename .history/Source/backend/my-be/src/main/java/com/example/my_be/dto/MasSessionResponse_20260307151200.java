package com.example.my_be.dto;

import java.time.LocalDateTime;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MasSessionResponse {
    private String sessionId;
    private String userId;
    private String conversationId;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
    public void setUserId(String userId) {
        this.userId = userId;
    }
    public void setConversationId(String conversationId) {
        this.conversationId = conversationId;
    }
    public void setStatus(String status) {
        this.status = status;
    }
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    public String getSessionId() {
        return sessionId;
    }
    public String getUserId() {
        return userId;
    }
    public String getConversationId() {
        return conversationId;
    }
    public String getStatus() {
        return status;
    }
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
}
