package com.example.my_be.dto;

import java.util.Date;

public class SummaryDifficultyAdjustmentDTO {
    private Long id;
    private String summaryId;
    private String createdByUserId;
    private Date createdAt;
    private String contentSummary;
    private String summaryIncrease;
    private String summaryDecrease;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getSummaryId() {
        return summaryId;
    }

    public void setSummaryId(String summaryId) {
        this.summaryId = summaryId;
    }

    public String getCreatedByUserId() {
        return createdByUserId;
    }

    public void setCreatedByUserId(String createdByUserId) {
        this.createdByUserId = createdByUserId;
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
