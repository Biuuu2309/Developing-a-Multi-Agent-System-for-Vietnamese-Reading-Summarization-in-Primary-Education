package com.example.my_be.model;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "messages")
@Data
@NoArgsConstructor
public class Message {
    @Id
    @Column(name = "message_id")
    private String messageId;

    @Column(name = "conversation_id")
    private String conversationId;

    @Column(name = "user_id")
    private String userId;

    @Column(name = "agent_id")
    private String agentId;

    @Enumerated(EnumType.STRING)
    @Column(name = "role")
    private MessageRole role;

    @Column(name = "content", columnDefinition = "TEXT")
    private String content;

    @Column(name = "metadata", columnDefinition = "JSON")
    private String metadata;

    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private MessageStatus status;

    @Column(name = "created_at")
    private String createdAt;

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").format(LocalDateTime.now());
        }
        if (status == null) {
            status = MessageStatus.PENDING;
        }
    }

    public enum MessageRole {
        USER, ASSISTANT, SYSTEM
    }

    public enum MessageStatus {
        PENDING, PROCESSING, COMPLETED, FAILED
    }
    
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
    public void setRole(MessageRole role) {
        this.role = role;
    }
    public void setContent(String content) {
        this.content = content;
    }
    public void setMetadata(String metadata) {
        this.metadata = metadata;
    }
    public void setStatus(MessageStatus status) {
        this.status = status;
    }
    public void setCreatedAt(String createdAt) {
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
    public MessageRole getRole() {
        return role;
    }
    public String getContent() {
        return content;
    }
    public String getMetadata() {
        return metadata;
    }
    public MessageStatus getStatus() {
        return status;
    }
    public LocalDateTime getCreatedAt() {
        return LocalDateTime.parse(createdAt);
    }
    public Message(String messageId, String conversationId, String userId, String agentId, MessageRole role, String content, String metadata, MessageStatus status, String createdAt) {
        this.messageId = messageId;
        this.conversationId = conversationId;
        this.userId = userId;
        this.agentId = agentId;
        this.role = role;
        this.content = content;
        this.metadata = metadata;
        this.status = status;
        this.createdAt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").format(LocalDateTime.now());
    }
}

