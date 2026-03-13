package com.example.my_be.service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.dto.MessageRequest;
import com.example.my_be.model.Message;
import com.example.my_be.repository.MessageRepository;

@Service
public class MessageService {
    @Autowired
    private MessageRepository messagerepository;
    public Message createRequest(MessageRequest request) {
        Message message = new Message();
        message.setMessageId(request.getMessage_id());
        message.setConversationId(request.getConversation_id());
        message.setUserId(request.getUser_id());
        message.setRole(Message.MessageRole.valueOf(request.getRole().toUpperCase()));
        message.setContent(request.getMessage());
        if (request.getCreated_at() != null && !request.getCreated_at().isEmpty()) {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
            message.setCreatedAt(LocalDateTime.parse(request.getCreated_at(), formatter));
        }
        return messagerepository.save(message);
    }
    public List<Message> getMessages() {
        return messagerepository.findAll();
    }
    public Optional<Message> getMessageById(String message_id) {
        return messagerepository.findById(message_id);
    }
    public void deleteMessage(String message_id) {
        messagerepository.deleteById(message_id);
    }
}
