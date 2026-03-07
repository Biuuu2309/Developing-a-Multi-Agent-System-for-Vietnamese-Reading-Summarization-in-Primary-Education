package com.example.my_be.controller;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.my_be.model.ReadHistory;
import com.example.my_be.model.Summary;
import com.example.my_be.model.User;
import com.example.my_be.repository.SummaryRepository;
import com.example.my_be.repository.UserRepository;
import com.example.my_be.service.ReadHistoryService;

@RestController
@RequestMapping("/api/read-history")
public class ReadHistoryController {

    @Autowired
    private ReadHistoryService readHistoryService;

    @Autowired
    private UserRepository userRepository; // To fetch user details by ID

    @Autowired
    private SummaryRepository summaryRepository; // To fetch summary details by ID

    // ReadHistoryDTO with added fields for title and imageUrl
    public static class ReadHistoryDTO {
        private Long id;
        private String userId;
        private String summaryId;
        private String title;      // Added field for title
        private String imageUrl;   // Added field for imageUrl
    
        // Constructor
        public ReadHistoryDTO(Long id, String userId, String summaryId, String title, String imageUrl) {
            this.id = id;
            this.userId = userId;
            this.summaryId = summaryId;
            this.title = title;
            this.imageUrl = imageUrl;
        }
    
        // Getters and Setters
        public Long getId() {
            return id;
        }
    
        public void setId(Long id) {
            this.id = id;
        }
    
        public String getUserId() {
            return userId;
        }
    
        public void setUserId(String userId) {
            this.userId = userId;
        }
    
        public String getSummaryId() {
            return summaryId;
        }
    
        public void setSummaryId(String summaryId) {
            this.summaryId = summaryId;
        }
    
        public String getTitle() {
            return title;
        }
    
        public void setTitle(String title) {
            this.title = title;
        }
    
        public String getImageUrl() {
            return imageUrl;
        }
    
        public void setImageUrl(String imageUrl) {
            this.imageUrl = imageUrl;
        }
    }
    

    // Endpoint to log a new read history
    @PostMapping("/log")
    public ResponseEntity<ReadHistory> logReadHistory(@RequestParam String userId, @RequestParam String summaryId) {
        // Fetch the user and summary by their IDs
        User user = userRepository.findById(userId).orElse(null);
        Summary summary = summaryRepository.findById(summaryId).orElse(null);

        if (user == null || summary == null) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND); // If either user or summary not found
        }

        // Log the read history
        ReadHistory readHistory = readHistoryService.logReadHistory(user, summary);

        return new ResponseEntity<>(readHistory, HttpStatus.CREATED);
    }

    // Get all ReadHistory by user
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<ReadHistoryDTO>> getReadHistoryByUser(@PathVariable String userId) {
        User user = userRepository.findById(userId).orElse(null);
    
        if (user == null) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND); // If user not found
        }
    
        List<ReadHistory> readHistories = readHistoryService.getReadHistoryByUser(user);
    
        // Convert ReadHistory to ReadHistoryDTO to avoid lazy-loaded fields
        List<ReadHistoryDTO> readHistoryDTOs = readHistories.stream()
            .map(readHistory -> {
                // Get the associated Summary
                Summary summary = readHistory.getSummary();
                return new ReadHistoryDTO(
                    readHistory.getId(),
                    readHistory.getUser().getUserId(),
                    readHistory.getSummary().getSummaryId(),
                    summary.getTitle(),
                    summary.getImageUrl()
                );
            })
            .collect(Collectors.toList());
    
        return new ResponseEntity<>(readHistoryDTOs, HttpStatus.OK);
    }
}
