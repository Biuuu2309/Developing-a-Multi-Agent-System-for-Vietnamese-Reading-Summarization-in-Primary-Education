package com.example.my_be.model;

import java.time.LocalDateTime;

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
@Table(name = "agent_logs")
@Data
@NoArgsConstructor
public class AgentLog {
    @Id
    @Column(name = "log_id")
    private String logId;

    @Column(name = "session_id")
    private String sessionId;

    @Column(name = "message_id")
    private String messageId;

    @Column(name = "agent_id")
    private String agentId;

    @Column(name = "input", columnDefinition = "TEXT")
    private String input;

    @Column(name = "output", columnDefinition = "TEXT")
    private String output;

    @Column(name = "duration_ms")
    private Integer durationMs;

    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private LogStatus status;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    public enum LogStatus {
        SUCCESS, ERROR
    }
    public void setLogId(String logId) {
        this.logId = logId;
    }
    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
    public void setMessageId(String messageId) {
        this.messageId = messageId;
    }
    public void setAgentId(String agentId) {
        this.agentId = agentId;
    }
    public void setInput(String input) {
        this.input = input;
    }
    public void setOutput(String output) {
        this.output = output;
    }
    public void setDurationMs(Integer durationMs) {
        this.durationMs = durationMs;
    }
    public void setStatus(LogStatus status) {
        this.status = status;
    }
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    public String getLogId() {
        return logId;
    }
    public String getSessionId() {
        return sessionId;
    }
    public String getMessageId() {
        return messageId;
    }
    public String getAgentId() {
        return agentId;
    }
    public String getInput() {
        return input;
    }
    public String getOutput() {
        return output;
    }
    public Integer getDurationMs() {
        return durationMs;
    }
    public LogStatus getStatus() {
        return status;
    }
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    public AgentLog(String logId, String messageId, String agentId, String input, String output, Integer durationMs, LogStatus status, LocalDateTime createdAt) {
        this.logId = logId;
        this.messageId = messageId;
        this.agentId = agentId;
        this.input = input;
        this.output = output;
        this.durationMs = durationMs;
        this.status = status;
        this.createdAt = createdAt;
    }
}

