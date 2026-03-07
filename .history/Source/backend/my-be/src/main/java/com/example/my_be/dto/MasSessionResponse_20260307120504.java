package com.example.my_be.dto;

import java.time.LocalDateTime;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MasSessionResponse {
    private String sessionId;
    private String userId;
    private String conversationId;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
