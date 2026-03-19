package com.example.my_be.dto;

public class SummaryHistoryDTO {
    private Long historyId;
    private String method;
    private String summaryContent;
    private boolean isAccepted;
    private Long sessionId;
    private String timestamp;
    private String userInput;
    private String summaryImageUrl;
    private String evaluation;
    private String masSessionId;
    private String conversationId;

    public String getUserInput() { return userInput; }
    public void setUserInput(String userInput) { this.userInput = userInput; }
    public String getSummaryImageUrl() { return summaryImageUrl; }
    public void setSummaryImageUrl(String summaryImageUrl) { this.summaryImageUrl = summaryImageUrl; }
    public String getEvaluation() { return evaluation; }
    public void setEvaluation(String evaluation) { this.evaluation = evaluation; }
    public String getMasSessionId() { return masSessionId; }
    public void setMasSessionId(String masSessionId) { this.masSessionId = masSessionId; }
    public String getConversationId() { return conversationId; }
    public void setConversationId(String conversationId) { this.conversationId = conversationId; }

    public Long getSessionId() {
        return sessionId;
    }

    public void setSessionId(Long sessionId) {
        this.sessionId = sessionId;
    }
    
    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
    public Long getHistoryId() {
        return historyId;
    }

    public void setHistoryId(Long historyId) {
        this.historyId = historyId;
    }

    public String getMethod() {
        return method;
    }

    public void setMethod(String method) {
        this.method = method;
    }

    public String getSummaryContent() {
        return summaryContent;
    }

    public void setSummaryContent(String summaryContent) {
        this.summaryContent = summaryContent;
    }

    public boolean getIsAccepted() {
        return isAccepted;
    }

    public void setIsAccepted(boolean isAccepted) {
        this.isAccepted = isAccepted;
    }

    // Getters and setters
}
