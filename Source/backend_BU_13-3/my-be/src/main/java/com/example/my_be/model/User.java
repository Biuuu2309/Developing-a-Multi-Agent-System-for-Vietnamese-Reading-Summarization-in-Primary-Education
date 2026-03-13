package com.example.my_be.model;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import com.fasterxml.jackson.annotation.JsonInclude;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)

public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    // hide it from the Swagger UI
    @Schema(accessMode = Schema.AccessMode.READ_ONLY)
    @Column(name = "user_id")
    private String userId;

    @Column(unique = true, nullable = false)
    private String username;

    @Column(nullable = false)
    private String password; // Will store the hashed password

    @Column(nullable = false)
    private String role; // Roles: CHILD, CONTRIBUTOR, ADMIN

    @Column(unique = true, nullable = false)
    private String email; // For communication and notifications

    private String fullName; // Optional field for personalization

    private String phoneNumber; // Optional field for contributors/admins

    private String avatarUrl; // Optional field for contributors/admins to upload their avatar

    private boolean isActive = true; // To manage account status (active/inactive)




    public void setPassword(String rawPassword, BCryptPasswordEncoder passwordEncoder) {
        this.password = passwordEncoder.encode(rawPassword);
    }

    public boolean checkPassword(String rawPassword, BCryptPasswordEncoder passwordEncoder) {
        return passwordEncoder.matches(rawPassword, this.password);
    }


    // get AvatarUrl
    public String getAvatarUrl() {
        return avatarUrl;
    }
}
