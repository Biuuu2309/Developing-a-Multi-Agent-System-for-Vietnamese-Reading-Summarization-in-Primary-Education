package com.example.my_be.repository;

import com.example.my_be.model.ReadHistory;
import com.example.my_be.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ReadHistoryRepository extends JpaRepository<ReadHistory, Long> {

    // Method to find read history by user
    List<ReadHistory> findByUser(User user);

}
