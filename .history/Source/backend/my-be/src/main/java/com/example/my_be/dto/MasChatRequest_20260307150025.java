package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MasChatRequest {
    private String sessionId;
    private String userId;
    private String userInput;
    private String conversationId;
    
}
