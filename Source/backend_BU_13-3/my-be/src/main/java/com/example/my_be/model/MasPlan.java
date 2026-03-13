package com.example.my_be.model;

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
@Table(name = "mas_plans")
@Data
@NoArgsConstructor
public class MasPlan {
    @Id
    @Column(name = "plan_id")
    private String planId;

    @ManyToOne
    @JoinColumn(name = "state_id", nullable = false)
    private MasState state;

    @Column(name = "intent", columnDefinition = "JSON")
    private String intent;

    @Column(name = "pipeline", columnDefinition = "JSON", nullable = false)
    private String pipeline;

    @Column(name = "context", columnDefinition = "JSON")
    private String context;

    @Column(name = "revision_count")
    private Integer revisionCount = 0;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
