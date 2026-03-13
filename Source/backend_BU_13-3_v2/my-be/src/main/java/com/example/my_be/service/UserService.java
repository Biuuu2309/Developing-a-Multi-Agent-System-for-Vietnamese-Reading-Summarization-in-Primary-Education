package com.example.my_be.service;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import com.example.my_be.model.User;
import com.example.my_be.repository.UserRepository;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;
    @Autowired
    private BCryptPasswordEncoder passwordEncoder;

    /**
     * Create a new user with a hashed password.
     */
    public User createUser(User user) {
        // Hash the user's password before saving
        if (user.getPassword() != null && !user.getPassword().isEmpty()) {
            user.setPassword(user.getPassword(), passwordEncoder);
        }
        return userRepository.save(user);
    }

    public User updateUserProfile(User user) {
        Optional<User> existingUserOpt = userRepository.findById(user.getUserId());
        if (existingUserOpt.isEmpty()) {
            return null; // or throw
        }
        User existing = existingUserOpt.get();
        // Update fields if provided
        if (user.getUsername() != null) existing.setUsername(user.getUsername());
        if (user.getEmail() != null) existing.setEmail(user.getEmail());
        if (user.getRole() != null) existing.setRole(user.getRole());
        if (user.getFullName() != null) existing.setFullName(user.getFullName());
        if (user.getPhoneNumber() != null) existing.setPhoneNumber(user.getPhoneNumber());
        if (user.getAvatarUrl() != null) existing.setAvatarUrl(user.getAvatarUrl());
        // Active flag if present (primitive boolean has default false if not sent)
        // Consider a DTO for partial updates; for now assume provided value should be applied when username provided
        existing.setActive(user.isActive());
        if (user.getPassword() != null && !user.getPassword().isEmpty()) {
            existing.setPassword(user.getPassword(), passwordEncoder);
        }
        return userRepository.save(existing);
    }
    
    /**
     * Get a user by their ID.
     */
    public Optional<User> getUserById(String userId) {
        return userRepository.findById(userId);
    }

    // Get all users by role
    public List<User> getUsersByRole(String role) {
        return userRepository.findByRole(role);
    }
    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }
    /**
     * Get a user by their username.
     */
    public Optional<User> getUserByUsername(String username) {
        return userRepository.findTop1ByUsername(username);
    }

    /**
     * Get all users in the system.
     */
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    /**
     * Delete a user by their ID.
     */
    public void deleteUser(String userId) {
        userRepository.deleteById(userId);
    }

    /**
     * Update a user's role to CONTRIBUTOR after their first approved summary.
     */
    public void promoteToContributor(User user) {
        if (!"CONTRIBUTOR".equals(user.getRole())) {
            user.setRole("CONTRIBUTOR");
            userRepository.save(user);
        }
    }

    public Optional<User> findByUsername(String username) {
        return userRepository.findTop1ByUsername(username);
    }
}
