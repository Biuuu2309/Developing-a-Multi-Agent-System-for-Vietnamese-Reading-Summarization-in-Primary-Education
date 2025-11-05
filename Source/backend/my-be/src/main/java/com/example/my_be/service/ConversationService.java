package com.example.my_be.service;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.dto.ConversationRequest;
import com.example.my_be.model.Conversation;
import com.example.my_be.repository.ConversationRepository;

@Service
public class ConversationService {
    @Autowired
    private ConversationRepository conversationRepository;
    public Conversation createConversation(ConversationRequest request) {
        Conversation conversation = new Conversation();
        conversation.setUser_id(request.getUser_id());
        conversation.setTitle(request.getTitle());
        conversation.setStatus(request.getStatus());
        conversation.setCreated_at(request.getCreated_at());
        conversation.setUpdated_at(request.getUpdated_at());
        return conversationRepository.save(conversation);
    }
    public List<Conversation> getConversations() {
        return conversationRepository.findAll();
    }
    public Optional<Conversation> getConversationById(String conversation_id) {
        return conversationRepository.findById(conversation_id);
    }
    public void deleteConversation(String conversation_id) {
        conversationRepository.deleteById(conversation_id);
    }
}
