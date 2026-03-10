package com.example.my_be.model;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "agents")
@Data
@NoArgsConstructor
public class Agent {
    @Id
    @Column(name = "agent_id")
    private String agentId;

    @Column(name = "name", length = 100)
    private String name;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "capabilities", columnDefinition = "JSON")
    private String capabilities;

    @Column(name = "agent_type")
    private AgentType agentType;

    @Column(name = "is_active")
    private Boolean isActive = true;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    public enum AgentType {
        INTENT, CLARIFICATION, PLANNING, IMAGE2TEXT, ABSTRACTER, EXTRACTOR, EVALUATION, ORCHESTRATOR, OTHER
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}

