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

import com.example.my_be.dto.CreateMessageRequest;
import com.example.my_be.dto.MessageResponse;
import com.example.my_be.model.Message;
import com.example.my_be.service.MessageNewService;
import com.example.my_be.service.MessageService;

@RestController
@RequestMapping("/api/message")
public class MessageController {
    @Autowired
    private MessageService messageService;
    
    @Autowired
    private MessageNewService messageNewService;
    
    @PostMapping("/create")
    public ResponseEntity<MessageResponse> createMessage(@RequestBody CreateMessageRequest request) {
        return new ResponseEntity<>(messageNewService.createMessage(request), HttpStatus.CREATED);
    }
    
    @GetMapping("/conversation/{conversationId}")
    public ResponseEntity<List<Message>> getMessagesByConversation(@PathVariable String conversationId) {
        return new ResponseEntity<>(messageNewService.getMessagesByConversation(conversationId), HttpStatus.OK);
    }
    
    @GetMapping("/new/{messageId}")
    public ResponseEntity<Message> getMessageById(@PathVariable String messageId) {
        return messageNewService.getMessageById(messageId)
            .map(body -> new ResponseEntity<>(body, HttpStatus.OK))
            .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
    
    @GetMapping
    public ResponseEntity<List<Message>> getMessages() {
        return new ResponseEntity<>(messageService.getMessages(), HttpStatus.OK);
    }
    
    @GetMapping("/old/{message_id}")
    public ResponseEntity<Message> getOldMessageById(@PathVariable("message_id") String message_id) {
        return messageService.getMessageById(message_id)
            .map(body -> new ResponseEntity<>(body, HttpStatus.OK))
            .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
    
    @DeleteMapping("/old/{message_id}")
    public ResponseEntity<Void> deleteMessage(@PathVariable("message_id") String message_id) {
        messageService.deleteMessage(message_id);
        return new ResponseEntity<>(HttpStatus.OK);
    }
}
