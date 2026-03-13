package com.example.my_be.model;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "mas_states")
@Data
@NoArgsConstructor
public class MasState {
    @Id
    @Column(name = "state_id")
    private String stateId;

    @ManyToOne
    @JoinColumn(name = "session_id", nullable = false)
    private MasSession session;

    @ManyToOne
    @JoinColumn(name = "message_id")
    private Message message;

    @Column(name = "user_input", columnDefinition = "TEXT")
    private String userInput;

    @Column(name = "history", columnDefinition = "JSON")
    private String history;

    @Column(name = "intent", columnDefinition = "JSON")
    private String intent;

    @Column(name = "clarification_needed")
    private Boolean clarificationNeeded = false;

    @Column(name = "clarification_question", columnDefinition = "TEXT")
    private String clarificationQuestion;

    @Column(name = "plan", columnDefinition = "JSON")
    private String plan;

    @Column(name = "original_text", columnDefinition = "TEXT")
    private String originalText;

    @Column(name = "summary", columnDefinition = "TEXT")
    private String summary;

    @Column(name = "evaluation", columnDefinition = "JSON")
    private String evaluation;

    @Column(name = "final_output", columnDefinition = "TEXT")
    private String finalOutput;

    @Column(name = "plan_revision_count")
    private Integer planRevisionCount = 0;

    @Column(name = "strategy_changed")
    private Boolean strategyChanged = false;

    @Column(name = "improvement_count")
    private Integer improvementCount = 0;

    @Column(name = "needs_improvement")
    private Boolean needsImprovement = false;

    @Column(name = "image_path", length = 500)
    private String imagePath;

    @Column(name = "extracted_text", columnDefinition = "TEXT")
    private String extractedText;

    @Column(name = "goal_state", columnDefinition = "JSON")
    private String goalState;

    @Column(name = "agent_confidences", columnDefinition = "JSON")
    private String agentConfidences;

    @Column(name = "negotiation_result", columnDefinition = "JSON")
    private String negotiationResult;

    @Column(name = "agent_memories", columnDefinition = "JSON")
    private String agentMemories;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
