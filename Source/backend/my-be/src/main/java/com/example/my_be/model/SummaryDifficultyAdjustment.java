package com.example.my_be.model;

import java.util.Date;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "summary_difficulty_adjustments")
public class SummaryDifficultyAdjustment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "summary_id", nullable = false)
    private Summary summary;

    @Column(name = "summary_id", insertable = false, updatable = false)
    private String summaryIdRef;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "created_by", nullable = false)
    private User createdBy;

    @Column(name = "created_by", insertable = false, updatable = false)
    private String createdByUserIdRef;

    @Column(nullable = false, updatable = false, columnDefinition = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    private Date createdAt;

    @Column(name = "content_summary", nullable = false, columnDefinition = "MEDIUMTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    private String contentSummary;

    @Column(name = "summary_increase", columnDefinition = "MEDIUMTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    private String summaryIncrease;

    @Column(name = "summary_decrease", columnDefinition = "MEDIUMTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    private String summaryDecrease;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Summary getSummary() {
        return summary;
    }

    public void setSummary(Summary summary) {
        this.summary = summary;
    }

    public User getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(User createdBy) {
        this.createdBy = createdBy;
    }

    public String getSummaryIdRef() {
        return summaryIdRef;
    }

    public void setSummaryIdRef(String summaryIdRef) {
        this.summaryIdRef = summaryIdRef;
    }

    public String getCreatedByUserIdRef() {
        return createdByUserIdRef;
    }

    public void setCreatedByUserIdRef(String createdByUserIdRef) {
        this.createdByUserIdRef = createdByUserIdRef;
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }

    public String getContentSummary() {
        return contentSummary;
    }

    public void setContentSummary(String contentSummary) {
        this.contentSummary = contentSummary;
    }

    public String getSummaryIncrease() {
        return summaryIncrease;
    }

    public void setSummaryIncrease(String summaryIncrease) {
        this.summaryIncrease = summaryIncrease;
    }

    public String getSummaryDecrease() {
        return summaryDecrease;
    }

    public void setSummaryDecrease(String summaryDecrease) {
        this.summaryDecrease = summaryDecrease;
    }
}
