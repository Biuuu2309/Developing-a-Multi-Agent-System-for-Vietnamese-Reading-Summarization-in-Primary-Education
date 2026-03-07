package com.example.my_be.service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.dto.MasSessionRequest;
import com.example.my_be.dto.MasSessionResponse;
import com.example.my_be.model.Conversation;
import com.example.my_be.model.MasSession;
import com.example.my_be.model.User;
import com.example.my_be.repository.ConversationRepository;
import com.example.my_be.repository.MasSessionRepository;
import com.example.my_be.repository.UserRepository;

@Service
public class MasSessionService {
    @Autowired
    private MasSessionRepository masSessionRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ConversationRepository conversationRepository;

    public MasSessionResponse createSession(MasSessionRequest request) {
        User user = userRepository.findById(request.getUserId())
            .orElseThrow(() -> new RuntimeException("User not found"));

        MasSession session = new MasSession();
        session.setSessionId(UUID.randomUUID().toString());
        session.setUser(user);
        session.setStatus(MasSession.SessionStatus.ACTIVE);

        if (request.getConversationId() != null) {
            Conversation conversation = conversationRepository.findById(request.getConversationId())
                .orElse(null);
            session.setConversation(conversation);
        }

        MasSession saved = masSessionRepository.save(session);
        return toResponse(saved);
    }

    public List<MasSessionResponse> getSessionsByUserId(String userId) {
        return masSessionRepository.findByUserUserId(userId)
            .stream()
            .map(this::toResponse)
            .collect(Collectors.toList());
    }

    public Optional<MasSessionResponse> getSessionById(String sessionId, String userId) {
        return masSessionRepository.findBySessionIdAndUserUserId(sessionId, userId)
            .map(this::toResponse);
    }

    public MasSessionResponse updateSessionStatus(String sessionId, MasSession.SessionStatus status) {
        MasSession session = masSessionRepository.findById(sessionId)
            .orElseThrow(() -> new RuntimeException("Session not found"));
        session.setStatus(status);
        MasSession updated = masSessionRepository.save(session);
        return toResponse(updated);
    }

    private MasSessionResponse toResponse(MasSession session) {
        MasSessionResponse response = new MasSessionResponse();
        response.setSessionId(session.getSessionId());
        response.setUserId(session.getUser().getUserId());
        response.setConversationId(session.getConversation() != null ? session.getConversation().getConversation_id() : null);
        response.setStatus(session.getStatus().name());
        response.setCreatedAt(session.getCreatedAt());
        response.setUpdatedAt(session.getUpdatedAt());
        return response;
    }
}
