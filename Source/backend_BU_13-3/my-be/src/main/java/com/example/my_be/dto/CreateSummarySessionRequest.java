// CreateSummarySessionRequest.java
package com.example.my_be.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateSummarySessionRequest {
    private String userId;
    private String content;
}
