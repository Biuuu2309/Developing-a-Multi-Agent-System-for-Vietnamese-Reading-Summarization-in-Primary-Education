package com.example.my_be.dto;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class MessageRequest {
    private String message_id;
    private String user_id;
    private String conversation_id;
    private String role;
    private String message;
    private String created_at;

    public MessageRequest() {
        this.created_at = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").format(LocalDateTime.now());
    }
    public void setMessage_id(String message_id) {
        this.message_id = message_id;
    }
    public void setUser_id(String user_id) {
        this.user_id = user_id;
    }
    public void setConversation_id(String conversation_id) {
        this.conversation_id = conversation_id;
    }
    public void setRole(String role) {
        this.role = role;
    }
    public void setMessage(String message) {
        this.message = message;
    }
    public void setCreated_at(String created_at) {
        if (created_at == null || created_at.isEmpty()) {
            this.created_at = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").format(LocalDateTime.now());
        } else {
            this.created_at = created_at;
        }
    }
    public String getUser_id() {
        return user_id;
    }
    public String getConversation_id() {
        return conversation_id;
    }
    public String getRole() {
        return role;
    }
    public String getMessage() {
        return message;
    }
    public String getMessage_id() {
        return message_id;
    }
    public String getCreated_at() {
        return created_at;
    }

    public MessageRequest(String message_id, String user_id, String conversation_id, String role, String message, String created_at) {
        this.message_id = message_id;
        this.conversation_id = conversation_id;
        this.role = role;
        this.user_id = user_id;
        this.message = message;
        this.created_at = created_at;
    }
}
