package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MasChatResponse {
    private String sessionId;
    private String stateId;
    private String messageId;
    private String finalOutput;
    private String intent;
    private String plan;
    private String summary;
    private String evaluation;
    private Boolean clarificationNeeded;
    private String clarificationQuestion;
    private String agentConfidences;
    private String status;
    private String summaryId;
    private String imageUrl;
    private String summaryImageUrl;
    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
    public void setStateId(String stateId) {
        this.stateId = stateId;
    }
    public void setMessageId(String messageId) {
        this.messageId = messageId;
    }
    public void setFinalOutput(String finalOutput) {
        this.finalOutput = finalOutput;
    }
    public void setIntent(String intent) {
        this.intent = intent;
    }
    public void setPlan(String plan) {
        this.plan = plan;
    }
    public void setSummary(String summary) {
        this.summary = summary;
    }
    public void setEvaluation(String evaluation) {
        this.evaluation = evaluation;
    }
    public void setClarificationNeeded(Boolean clarificationNeeded) {
        this.clarificationNeeded = clarificationNeeded;
    }
    public void setClarificationQuestion(String clarificationQuestion) {
        this.clarificationQuestion = clarificationQuestion;
    }
    public void setAgentConfidences(String agentConfidences) {
        this.agentConfidences = agentConfidences;
    }
    public void setStatus(String status) {
        this.status = status;
    }
    public String getSessionId() {
        return sessionId;
    }
    public String getStateId() {
        return stateId;
    }
    public String getMessageId() {
        return messageId;
    }
    public String getFinalOutput() {
        return finalOutput;
    }
    public String getIntent() {
        return intent;
    }
    public String getPlan() {
        return plan;
    }
    public String getSummary() {
        return summary;
    }
    public String getEvaluation() {
        return evaluation;
    }
    public Boolean getClarificationNeeded() {
        return clarificationNeeded;
    }
    public String getClarificationQuestion() {
        return clarificationQuestion;
    }
    public String getAgentConfidences() {
        return agentConfidences;
    }
    public String getStatus() {
        return status;
    }
    public void setSummaryId(String summaryId) {
        this.summaryId = summaryId;
    }
    public String getSummaryId() {
        return summaryId;
    }
    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }
    public String getImageUrl() {
        return imageUrl;
    }
    public void setSummaryImageUrl(String summaryImageUrl) {
        this.summaryImageUrl = summaryImageUrl;
    }
    public String getSummaryImageUrl() {
        return summaryImageUrl;
    }
}
