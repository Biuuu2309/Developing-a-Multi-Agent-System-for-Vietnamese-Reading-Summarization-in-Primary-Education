package com.example.my_be.controller;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.my_be.dto.LoginRequest;
import com.example.my_be.dto.UserResponse;
import com.example.my_be.model.User;
import com.example.my_be.service.UserService;

@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    @Autowired
    private BCryptPasswordEncoder passwordEncoder;

    // Get all users
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.getAllUsers();
        return new ResponseEntity<>(users, HttpStatus.OK);
    }

    // Get a user by ID
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable String id) {
        Optional<User> user = userService.getUserById(id);
        return user.map(value -> new ResponseEntity<>(value, HttpStatus.OK))
                .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    // Create a new user
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        User savedUser = userService.createUser(user);
        return new ResponseEntity<>(savedUser, HttpStatus.CREATED);
    }

    @PutMapping("/{id}/profile")
    public ResponseEntity<User> updateProfile(@PathVariable("id") String id, @RequestBody User user) {
        System.out.println("Received PUT request for ID: " + id);
        System.out.println("Request body: " + user);
        user.setUserId(id);
        User updatedUser = userService.updateUserProfile(user);
        if (updatedUser != null) {
            return new ResponseEntity<>(updatedUser, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }
    // Update an existing user
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable String id, @RequestBody User user) {
        Optional<User> existingUser = userService.getUserById(id);
        if (existingUser.isPresent()) {
            user.setUserId(id); // Ensure the ID is not changed
            User updatedUser = userService.createUser(user);
            return new ResponseEntity<>(updatedUser, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }
    // Login endpoint
    @PostMapping("/auth/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest loginRequest) {
        Optional<User> userOptional = userService.findByUsername(loginRequest.getUsername());

        if (userOptional.isPresent()) {
            User user = userOptional.get();

            boolean passwordMatches = user.checkPassword(loginRequest.getPassword(), passwordEncoder);

            if (passwordMatches) {
                UserResponse userResponse = new UserResponse();
                userResponse.setUserId(user.getUserId());
                userResponse.setUsername(user.getUsername());
                userResponse.setEmail(user.getEmail());
                userResponse.setRole(user.getRole());
                userResponse.setFullName(user.getFullName());
                userResponse.setPhoneNumber(user.getPhoneNumber());
                userResponse.setAvatarUrl(user.getAvatarUrl());

                return new ResponseEntity<>(userResponse, HttpStatus.OK);
            }
        }

        return new ResponseEntity<>("Invalid username or password", HttpStatus.UNAUTHORIZED);
    }
    // Delete a user by ID
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable String id) {
        userService.deleteUser(id);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    // Get users by role (e.g., CHILD, CONTRIBUTOR)
    @GetMapping("/role/{role}")
    public ResponseEntity<List<User>> getUsersByRole(@PathVariable String role) {
        List<User> users = userService.getUsersByRole(role);
        return new ResponseEntity<>(users, HttpStatus.OK);
    }

    // Update a user's avatar URL
    @PutMapping("/{id}/avatar")
    public ResponseEntity<Void> updateAvatar(@PathVariable String id, @RequestBody Map<String, String> request) {
        String avatarUrl = request.get("avatarUrl");
        Optional<User> optionalUser = userService.getUserById(id);
        if (optionalUser.isPresent()) {
            User user = optionalUser.get();
            user.setAvatarUrl(avatarUrl); // Update avatar URL
            userService.createUser(user); // Save changes
            return new ResponseEntity<>(HttpStatus.OK);
        } else {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }
}
