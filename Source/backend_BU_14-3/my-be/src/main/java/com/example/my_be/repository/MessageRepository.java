package com.example.my_be.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.Message;

@Repository
public interface MessageRepository extends JpaRepository<Message, String> {
    
}
