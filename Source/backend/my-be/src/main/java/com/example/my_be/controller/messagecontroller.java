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

import com.example.my_be.dto.MessageRequest;
import com.example.my_be.model.MessageUserAi;
import com.example.my_be.service.MessageService;

@RestController
@RequestMapping("/api/message")
public class MessageController {
    @Autowired
    private MessageService messageService;
    @PostMapping("/create")
    public ResponseEntity<MessageUserAi> createMessage(@RequestBody MessageRequest request) {
        return new ResponseEntity<>(messageService.createRequest(request), HttpStatus.CREATED);
    }
    @GetMapping
    public ResponseEntity<List<MessageUserAi>> getMessages() {
        return new ResponseEntity<>(messageService.getMessages(), HttpStatus.OK);
    }
    @GetMapping("/{message_id}")
    public ResponseEntity<MessageUserAi> getMessageById(@PathVariable("message_id") String message_id) {
        return messageService.getMessageById(message_id)
            .map(body -> new ResponseEntity<>(body, HttpStatus.OK))
            .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
    @DeleteMapping("/{message_id}")
    public ResponseEntity<Void> deleteMessage(@PathVariable("message_id") String message_id) {
        messageService.deleteMessage(message_id);
        return new ResponseEntity<>(HttpStatus.OK);
    }
}
