package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MASResponse {
    private String response;
    private String agentId;
    private String metadata;
    private String role;
    public void setResponse(String response) {
        this.response = response;
    }
    public void setAgentId(String agentId) {
        this.agentId = agentId;
    }
    public void setMetadata(String metadata) {
        this.metadata = metadata;
    }
    public void setRole(String role) {
        this.role = role;
    }
    public String getResponse() {
        return response;
    }
    public String getAgentId() {
        return agentId;
    }
    public String getMetadata() {
        return metadata;
    }
    public String getRole() {
        return role;
    }
}

