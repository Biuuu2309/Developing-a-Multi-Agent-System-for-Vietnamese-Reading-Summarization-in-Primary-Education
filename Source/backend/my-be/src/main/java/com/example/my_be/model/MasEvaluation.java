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

    // Text difficulty features (map 1-1 với mas_evaluations table)
    @Column(name = "difficulty_level", length = 50)
    private String difficultyLevel;

    @Column(name = "total_words")
    private Integer totalWords;

    @Column(name = "unique_words")
    private Integer uniqueWords;

    @Column(name = "type_token_ratio", precision = 5, scale = 4)
    private BigDecimal typeTokenRatio;

    @Column(name = "rare_word_ratio", precision = 5, scale = 4)
    private BigDecimal rareWordRatio;

    @Column(name = "unknown_word_ratio", precision = 5, scale = 4)
    private BigDecimal unknownWordRatio;

    @Column(name = "avg_word_grade", precision = 6, scale = 3)
    private BigDecimal avgWordGrade;

    @Column(name = "num_sentences")
    private Integer numSentences;

    @Column(name = "avg_sentence_length", precision = 6, scale = 2)
    private BigDecimal avgSentenceLength;

    @Column(name = "max_sentence_length")
    private Integer maxSentenceLength;

    @Column(name = "min_sentence_length")
    private Integer minSentenceLength;

    @Column(name = "long_sentence_ratio", precision = 5, scale = 4)
    private BigDecimal longSentenceRatio;

    @Column(name = "avg_word_length", precision = 6, scale = 3)
    private BigDecimal avgWordLength;

    @Column(name = "words_per_sentence", precision = 6, scale = 2)
    private BigDecimal wordsPerSentence;

    @Column(name = "lexical_density", precision = 5, scale = 4)
    private BigDecimal lexicalDensity;

    @Column(name = "matched_rules", columnDefinition = "TEXT")
    private String matchedRules;

    @Column(name = "comment", columnDefinition = "TEXT")
    private String comment;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
