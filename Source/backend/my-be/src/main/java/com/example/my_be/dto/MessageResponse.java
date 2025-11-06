package com.example.my_be.dto;

import java.time.LocalDateTime;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MessageResponse {
    private String messageId;
    private String conversationId;
    private String userId;
    private String agentId;
    private String role;
    private String content;
    private String metadata;
    private String status;
    private LocalDateTime createdAt;
    public void setMessageId(String messageId) {
        this.messageId = messageId;
    }
    public void setConversationId(String conversationId) {
        this.conversationId = conversationId;
    }
    public void setUserId(String userId) {
        this.userId = userId;
    }
    public void setAgentId(String agentId) {
        this.agentId = agentId;
    }
    public void setRole(String role) {
        this.role = role;
    }
    public void setContent(String content) {
        this.content = content;
    }
    public void setMetadata(String metadata) {
        this.metadata = metadata;
    }
    public void setStatus(String status) {
        this.status = status;
    }
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    public String getMessageId() {
        return messageId;
    }
    public String getConversationId() {
        return conversationId;
    }
    public String getUserId() {
        return userId;
    }
    public String getAgentId() {
        return agentId;
    }
    public String getRole() {
        return role;
    }
    public String getContent() {
        return content;
    }
    public String getMetadata() {
        return metadata;
    }
    public String getStatus() {
        return status;
    }
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}

