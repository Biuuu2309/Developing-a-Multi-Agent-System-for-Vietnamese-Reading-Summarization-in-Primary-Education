package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.MasNegotiation;

@Repository
public interface MasNegotiationRepository extends JpaRepository<MasNegotiation, String> {
    List<MasNegotiation> findBySessionSessionId(String sessionId);
    Optional<MasNegotiation> findByNegotiationIdAndSessionSessionId(String negotiationId, String sessionId);
}
