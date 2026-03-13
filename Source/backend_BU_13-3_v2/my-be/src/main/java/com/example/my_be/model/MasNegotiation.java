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
@Table(name = "mas_negotiations")
@Data
@NoArgsConstructor
public class MasNegotiation {
    @Id
    @Column(name = "negotiation_id")
    private String negotiationId;

    @ManyToOne
    @JoinColumn(name = "session_id", nullable = false)
    private MasSession session;

    @Column(name = "initiator", length = 100, nullable = false)
    private String initiator;

    @Column(name = "participants", columnDefinition = "JSON", nullable = false)
    private String participants;

    @Column(name = "topic", length = 255)
    private String topic;

    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private NegotiationStatus status;

    @Column(name = "proposals", columnDefinition = "JSON")
    private String proposals;

    @Column(name = "responses", columnDefinition = "JSON")
    private String responses;

    @Column(name = "constraints", columnDefinition = "JSON")
    private String constraints;

    @Column(name = "max_rounds")
    private Integer maxRounds = 5;

    @Column(name = "current_round")
    private Integer currentRound = 1;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (status == null) {
            status = NegotiationStatus.INITIATED;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public enum NegotiationStatus {
        INITIATED, IN_PROGRESS, ACCEPTED, REJECTED, TIMEOUT
    }
}
