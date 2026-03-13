package com.example.my_be.model;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "mas_agent_confidences")
@Data
@NoArgsConstructor
public class MasAgentConfidence {
    @Id
    @Column(name = "confidence_id")
    private String confidenceId;

    @ManyToOne
    @JoinColumn(name = "agent_id", nullable = false)
    private Agent agent;

    @ManyToOne
    @JoinColumn(name = "session_id")
    private MasSession session;

    @Column(name = "task_type", length = 100)
    private String taskType;

    @Column(name = "confidence_score", precision = 5, scale = 4, nullable = false)
    private BigDecimal confidenceScore;

    @Column(name = "context", columnDefinition = "JSON")
    private String context;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
