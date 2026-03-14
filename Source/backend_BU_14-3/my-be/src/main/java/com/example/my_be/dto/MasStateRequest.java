package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MasStateRequest {
    private String sessionId;
    private String messageId;
    private String userInput;
    private String history;
    private String intent;
    private Boolean clarificationNeeded;
    private String clarificationQuestion;
    private String plan;
    private String originalText;
    private String summary;
    private String evaluation;
    private String finalOutput;
    private Integer planRevisionCount;
    private Boolean strategyChanged;
    private Integer improvementCount;
    private Boolean needsImprovement;
    private String imagePath;
    private String extractedText;
    private String goalState;
    private String agentConfidences;
    private String negotiationResult;
    private String agentMemories;
    private String semanticRecall;
    private String toolRecommendations;
    private String knowledgeSearch;
    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
    public void setMessageId(String messageId) {
        this.messageId = messageId;
    }
    public void setUserInput(String userInput) {
        this.userInput = userInput;
    }
    public void setHistory(String history) {
        this.history = history;
    }
    public void setIntent(String intent) {
        this.intent = intent;
    }
    public void setClarificationNeeded(Boolean clarificationNeeded) {
        this.clarificationNeeded = clarificationNeeded;
    }
    public void setClarificationQuestion(String clarificationQuestion) {
        this.clarificationQuestion = clarificationQuestion;
    }
    public void setPlan(String plan) {
        this.plan = plan;
    }
    public void setOriginalText(String originalText) {
        this.originalText = originalText;
    }
    public void setSummary(String summary) {
        this.summary = summary;
    }
    public void setEvaluation(String evaluation) {
        this.evaluation = evaluation;
    }
    public void setFinalOutput(String finalOutput) {
        this.finalOutput = finalOutput;
    }
    public void setPlanRevisionCount(Integer planRevisionCount) {
        this.planRevisionCount = planRevisionCount;
    }
    public void setStrategyChanged(Boolean strategyChanged) {
        this.strategyChanged = strategyChanged;
    }
    public void setImprovementCount(Integer improvementCount) {
        this.improvementCount = improvementCount;
    }
    public void setNeedsImprovement(Boolean needsImprovement) {
        this.needsImprovement = needsImprovement;
    }
    public void setImagePath(String imagePath) {
        this.imagePath = imagePath;
    }
    public void setExtractedText(String extractedText) {
        this.extractedText = extractedText;
    }
    public void setGoalState(String goalState) {
        this.goalState = goalState;
    }
    public void setAgentConfidences(String agentConfidences) {
        this.agentConfidences = agentConfidences;
    }
    public void setNegotiationResult(String negotiationResult) {
        this.negotiationResult = negotiationResult;
    }
    public void setAgentMemories(String agentMemories) {
        this.agentMemories = agentMemories;
    }
    public String getSessionId() {
        return sessionId;
    }
    public String getMessageId() {
        return messageId;
    }
    public String getUserInput() {
        return userInput;
    }
    public String getHistory() {
        return history;
    }
    public String getIntent() {
        return intent;
    }
    public Boolean getClarificationNeeded() {
        return clarificationNeeded;
    }
    public String getClarificationQuestion() {
        return clarificationQuestion;
    }
    public String getPlan() {
        return plan;
    }
    public String getOriginalText() {
        return originalText;
    }
    public String getSummary() {
        return summary;
    }
    public String getEvaluation() {
        return evaluation;
    }
    public String getFinalOutput() {
        return finalOutput;
    }
    public Integer getPlanRevisionCount() {
        return planRevisionCount;
    }
    public Boolean getStrategyChanged() {
        return strategyChanged;
    }
    public Integer getImprovementCount() {
        return improvementCount;
    }
    public Boolean getNeedsImprovement() {
        return needsImprovement;
    }
    public String getImagePath() {
        return imagePath;
    }
    public String getExtractedText() {
        return extractedText;
    }
    public String getGoalState() {
        return goalState;
    }
    public String getAgentConfidences() {
        return agentConfidences;
    }
    public String getNegotiationResult() {
        return negotiationResult;
    }
    public String getAgentMemories() {
        return agentMemories;
    }
    public void setSemanticRecall(String semanticRecall) {
        this.semanticRecall = semanticRecall;
    }
    public String getSemanticRecall() {
        return semanticRecall;
    }
    public void setToolRecommendations(String toolRecommendations) {
        this.toolRecommendations = toolRecommendations;
    }
    public String getToolRecommendations() {
        return toolRecommendations;
    }
    public void setKnowledgeSearch(String knowledgeSearch) {
        this.knowledgeSearch = knowledgeSearch;
    }
    public String getKnowledgeSearch() {
        return knowledgeSearch;
    }
}
