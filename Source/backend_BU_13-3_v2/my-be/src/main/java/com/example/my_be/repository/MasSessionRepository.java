package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.MasSession;

@Repository
public interface MasSessionRepository extends JpaRepository<MasSession, String> {
    List<MasSession> findByUserUserId(String userId);
    List<MasSession> findByUserUserIdAndStatus(String userId, MasSession.SessionStatus status);
    Optional<MasSession> findBySessionIdAndUserUserId(String sessionId, String userId);
}
