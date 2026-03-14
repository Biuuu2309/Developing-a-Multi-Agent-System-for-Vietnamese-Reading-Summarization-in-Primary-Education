package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MASRequest {
    private String conversationId;
    private String userId;
    private String content;
    private String messageId;
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
    public void setMessageId(String messageId) {
        this.messageId = messageId;
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
    public String getMessageId() {
        return messageId;
    }
    public String getRole() {
        return role;
    }
}

