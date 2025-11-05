package com.example.my_be.dto;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class ConversationRequest {
    private String user_id;
    private String title;
    private String status;
    private String created_at;
    private String updated_at;
    public ConversationRequest() {
        this.created_at = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").format(LocalDateTime.now());
        this.updated_at = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").format(LocalDateTime.now());
    }
    public void setUser_id(String user_id) {
        this.user_id = user_id;
    }
    public void setTitle(String title) {
        this.title = title;
    }
    public void setStatus(String status) {
        this.status = status;
    }
    public void setCreated_at(String created_at) {
        if (created_at == null || created_at.isEmpty()) {
            this.created_at = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").format(LocalDateTime.now());
        } else {
            this.created_at = created_at;
        }
    }
    public void setUpdated_at(String updated_at) {
        if (updated_at == null || updated_at.isEmpty()) {
            this.updated_at = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").format(LocalDateTime.now());
        } else {
            this.updated_at = updated_at;
        }
    }
    public String getUser_id() {
        return user_id;
    }
    public String getTitle() {
        return title;
    }
    public String getStatus() {
        return status;
    }
    public String getCreated_at() {
        return created_at;
    }
    public String getUpdated_at() {
        return updated_at;
    }
    public ConversationRequest(String user_id, String title, String status, String created_at, String updated_at) {
        this.user_id = user_id;
        this.title = title;
        this.status = status;
        this.created_at = created_at;
        this.updated_at = updated_at;
    }
}
