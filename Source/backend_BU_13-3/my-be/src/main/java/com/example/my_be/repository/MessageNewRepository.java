package com.example.my_be.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.Message;

@Repository
public interface MessageNewRepository extends JpaRepository<Message, String> {
    List<Message> findByConversationId(String conversationId);
    List<Message> findByUserId(String userId);
}

