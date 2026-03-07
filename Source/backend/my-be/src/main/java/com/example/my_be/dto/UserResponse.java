package com.example.my_be.dto;

import lombok.Data;

@Data
public class UserResponse {
    private String userId;
    private String username;
    private String email;
    private String role;
    private String fullName;
    private String phoneNumber;
    private String avatarUrl;
    private boolean isActive;
}
