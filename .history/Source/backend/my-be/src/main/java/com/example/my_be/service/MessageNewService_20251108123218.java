package com.example.my_be.service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import com.example.my_be.dto.CreateMessageRequest;
import com.example.my_be.dto.MASRequest;
import com.example.my_be.dto.MASResponse;
import com.example.my_be.dto.MessageResponse;
import com.example.my_be.model.Message;
import com.example.my_be.model.Message.MessageRole;
import com.example.my_be.model.Message.MessageStatus;
import com.example.my_be.repository.MessageNewRepository;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MessageNewService {
    @Autowired
    private MessageNewRepository messageRepository;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    @Value("${mas.api.url:http://localhost:8000/process}")
    private String masApiUrl;

    @Transactional
    public MessageResponse createMessage(CreateMessageRequest request) {
        String messageId = UUID.randomUUID().toString();
        
        Message userMessage = new Message();
        userMessage.setMessageId(messageId);
        userMessage.setConversationId(request.getConversationId());
        userMessage.setUserId(request.getUserId());
        userMessage.setAgentId(request.getAgentId());
        userMessage.setRole(MessageRole.USER);
        userMessage.setContent(request.getContent());
        userMessage.setMetadata(request.getMetadata());
        userMessage.setStatus(MessageStatus.PENDING);
        
        Message savedMessage = messageRepository.save(userMessage);
        
        try {
            MASRequest masRequest = new MASRequest();
            masRequest.setConversationId(request.getConversationId());
            masRequest.setUserId(request.getUserId());
            masRequest.setContent(request.getContent());
            masRequest.setMessageId(messageId);
            masRequest.setRole(request.getRole());
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            String json = objectMapper.writeValueAsString(masRequest);
            HttpEntity<String> entity = new HttpEntity<>(json, headers);
            
            savedMessage.setStatus(MessageStatus.PROCESSING);
            messageRepository.save(savedMessage);
            
            System.out.println("MAS API URL: " + masApiUrl);
            System.out.println("MAS API entity: " + entity);
            ResponseEntity<String> response = restTemplate.postForEntity(masApiUrl, entity, String.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                MASResponse masResponse = objectMapper.readValue(response.getBody(), MASResponse.class);
                
                Message assistantMessage = new Message();
                assistantMessage.setMessageId(UUID.randomUUID().toString());
                assistantMessage.setConversationId(request.getConversationId());
                assistantMessage.setUserId(request.getUserId());
                assistantMessage.setAgentId(masResponse.getAgentId());
                assistantMessage.setRole(MessageRole.ASSISTANT);
                assistantMessage.setContent(masResponse.getResponse());
                assistantMessage.setMetadata(masResponse.getMetadata());
                assistantMessage.setStatus(MessageStatus.COMPLETED);
                
                messageRepository.save(assistantMessage);
                
                savedMessage.setStatus(MessageStatus.COMPLETED);
                messageRepository.save(savedMessage);
            } else {
                savedMessage.setStatus(MessageStatus.FAILED);
                messageRepository.save(savedMessage);
            }
        } catch (Exception e) {
            System.err.println("Error calling MAS API: " + e.getMessage());
            e.printStackTrace();
            savedMessage.setStatus(MessageStatus.FAILED);
            messageRepository.save(savedMessage);
        }
        
        return mapToResponse(savedMessage);
    }

    public List<Message> getMessagesByConversation(String conversationId) {
        return messageRepository.findByConversationId(conversationId);
    }

    public Optional<Message> getMessageById(String messageId) {
        return messageRepository.findById(messageId);
    }

    public List<Message> getMessagesByUser(String userId) {
        return messageRepository.findByUserId(userId);
    }

    private MessageResponse mapToResponse(Message message) {
        MessageResponse response = new MessageResponse();
        response.setMessageId(message.getMessageId());
        response.setConversationId(message.getConversationId());
        response.setUserId(message.getUserId());
        response.setAgentId(message.getAgentId());
        response.setRole(message.getRole().name());
        response.setContent(message.getContent());
        response.setMetadata(message.getMetadata());
        response.setStatus(message.getStatus().name());
        response.setCreatedAt(message.getCreatedAt());
        return response;
    }
}

