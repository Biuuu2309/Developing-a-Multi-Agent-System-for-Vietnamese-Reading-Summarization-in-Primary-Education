package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class CreateAgentLogRequest {
    private String messageId;
    private String agentId;
    private String input;
    private String output;
    private Integer durationMs;
    private String status;
}

