package com.example.my_be.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.my_be.dto.ConversationRequest;
import com.example.my_be.model.Conversation;
import com.example.my_be.service.ConversationService;

@RestController
@RequestMapping("/api/conversations")
public class ConversationController {
    @Autowired
    private ConversationService conversationService;
    @PostMapping("/create")
    public ResponseEntity<Conversation> createConversation(@RequestBody ConversationRequest request) {
        return new ResponseEntity<>(conversationService.createConversation(request), HttpStatus.CREATED);
    }
    @GetMapping
    public ResponseEntity<List<Conversation>> getConversations() {
        return new ResponseEntity<>(conversationService.getConversations(), HttpStatus.OK);
    }
    @GetMapping("/{conversation_id}")
    public ResponseEntity<Conversation> getConversationById(@PathVariable String conversation_id) {
        return conversationService.getConversationById(conversation_id)
            .map(body -> new ResponseEntity<>(body, HttpStatus.OK))
            .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
    @DeleteMapping("/{conversation_id}")
    public ResponseEntity<Void> deleteConversation(@PathVariable String conversation_id) {
        conversationService.deleteConversation(conversation_id);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
