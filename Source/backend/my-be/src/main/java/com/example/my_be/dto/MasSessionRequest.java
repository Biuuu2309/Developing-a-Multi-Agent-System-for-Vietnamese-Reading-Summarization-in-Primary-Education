package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MasSessionRequest {
    private String userId;
    private String conversationId;
    public void setUserId(String userId) {
        this.userId = userId;
    }
    public void setConversationId(String conversationId) {
        this.conversationId = conversationId;
    }
    public String getUserId() {
        return userId;
    }
    public String getConversationId() {
        return conversationId;
    }
}
