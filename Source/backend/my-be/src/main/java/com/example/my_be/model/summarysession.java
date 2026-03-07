package com.example.my_be.model;


import java.util.Date;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Lob;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "summary_sessions")
@Data
@NoArgsConstructor

public class SummarySession {
    @Column(nullable = false)
    private String contentHash;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long sessionId; // Unique ID for the session

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "created_by", referencedColumnName = "user_id", nullable = false, columnDefinition = "varchar(255)")
    private User createdBy; // User who initiated this summary session

    @Column(nullable = false, columnDefinition = "MEDIUMTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    @Lob
    private String content; // Optional image URL associated with this session

    @Column(nullable = false)
    private String timestamp = new Date().toString(); // Persisted timestamp with default value

    // Getters and setters
    public Long getSessionId() {
        return sessionId;
    }

    public void setSessionId(Long sessionId) {
        this.sessionId = sessionId;
    }

    public User getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(User createdBy) {
        this.createdBy = createdBy;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getContentHash() {
        return contentHash;
    }

    public void setContentHash(String contentHash) {
        this.contentHash = contentHash;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}
