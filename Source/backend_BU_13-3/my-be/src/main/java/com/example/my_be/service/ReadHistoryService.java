package com.example.my_be.service;

import com.example.my_be.model.ReadHistory;
import com.example.my_be.model.Summary;
import com.example.my_be.model.User;
import com.example.my_be.repository.ReadHistoryRepository;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class ReadHistoryService {

    @Autowired
    private ReadHistoryRepository readHistoryRepository;

    // Method to log the read history
    public ReadHistory logReadHistory(User user, Summary summary) {
        // Create a new ReadHistory record
        ReadHistory readHistory = new ReadHistory();
        readHistory.setUser(user);
        readHistory.setSummary(summary);

        // Save and return the ReadHistory entity
        return readHistoryRepository.save(readHistory);
    }

    public List<ReadHistory> getReadHistoryByUser(User user) {
        // Explicitly fetch user and summary in the service layer
        List<ReadHistory> histories = readHistoryRepository.findByUser(user);
        
        // Optionally, initialize the relationships
        for (ReadHistory history : histories) {
            history.getUser().getUsername(); // Force initialization of the user
            history.getSummary().getTitle(); // Force initialization of the summary
        }
        return histories;
    }
    
}
