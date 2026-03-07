package com.example.my_be.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MasSessionRequest {
    private String userId;
    private String conversationId;
}
