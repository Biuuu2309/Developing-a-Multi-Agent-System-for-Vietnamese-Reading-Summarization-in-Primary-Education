package com.example.my_be.model;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "mas_goals")
@Data
@NoArgsConstructor
public class MasGoal {
    @Id
    @Column(name = "goal_id")
    private String goalId;

    @ManyToOne
    @JoinColumn(name = "session_id", nullable = false)
    private MasSession session;

    @Column(name = "goal_type", length = 100, nullable = false)
    private String goalType;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "requirements", columnDefinition = "JSON")
    private String requirements;

    @Column(name = "priority")
    private Integer priority = 5;

    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private GoalStatus status;

    @Column(name = "progress", columnDefinition = "JSON")
    private String progress;

    @Column(name = "final_metrics", columnDefinition = "JSON")
    private String finalMetrics;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (status == null) {
            status = GoalStatus.PENDING;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public enum GoalStatus {
        PENDING, IN_PROGRESS, ACHIEVED, FAILED, CANCELLED
    }
}
