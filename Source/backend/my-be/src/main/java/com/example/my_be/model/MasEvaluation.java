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
@Table(name = "mas_evaluations")
@Data
@NoArgsConstructor
public class MasEvaluation {
    @Id
    @Column(name = "evaluation_id")
    private String evaluationId;

    @ManyToOne
    @JoinColumn(name = "state_id", nullable = false)
    private MasState state;

    @Column(name = "metrics", columnDefinition = "JSON", nullable = false)
    private String metrics;

    @Column(name = "rouge1_f1", precision = 5, scale = 4)
    private BigDecimal rouge1F1;

    @Column(name = "rougeL_f1", precision = 5, scale = 4)
    private BigDecimal rougeLF1;

    @Column(name = "bertscore_f1", precision = 5, scale = 4)
    private BigDecimal bertscoreF1;

    @Column(name = "comment", columnDefinition = "TEXT")
    private String comment;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
