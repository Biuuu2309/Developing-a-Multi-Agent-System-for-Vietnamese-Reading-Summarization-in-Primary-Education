package com.example.my_be.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "conversations")
public class Conversation {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String conversation_id;
    private String user_id;
    private String title;
    private String status;
    private String created_at;
    private String updated_at;

    public Conversation() { }
    public void setConversation_id(String conversation_id) {
        this.conversation_id = conversation_id;
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
        this.created_at = created_at;
    }
    public void setUpdated_at(String updated_at) {
        this.updated_at = updated_at;
    }
    public String getConversation_id() {
        return conversation_id;
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
    public Conversation(String conversation_id, String user_id, String title, String status, String created_at, String updated_at) {
        this.conversation_id = conversation_id;
        this.user_id = user_id;
        this.title = title;
        this.status = status;
        this.created_at = created_at;
        this.updated_at = updated_at;
    }
}
