package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class CreateMessageRequest {
    private String conversationId;
    private String userId;
    private String content;
    private String agentId;
    private String metadata;
    private String role;
    public void setConversationId(String conversationId) {
        this.conversationId = conversationId;
    }
    public void setUserId(String userId) {
        this.userId = userId;
    }
    public void setContent(String content) {
        this.content = content;
    }
    public void setAgentId(String agentId) {
        this.agentId = agentId;
    }
    public void setMetadata(String metadata) {
        this.metadata = metadata;
    }
    public void setRole(String role) {
        this.role = role;
    }
    public String getConversationId() {
        return conversationId;
    }
    public String getUserId() {
        return userId;
    }
    public String getContent() {
        return content;
    }
    public String getAgentId() {
        return agentId;
    }
    public String getMetadata() {
        return metadata;
    }
    public String getRole() {
        return role;
    }
}

