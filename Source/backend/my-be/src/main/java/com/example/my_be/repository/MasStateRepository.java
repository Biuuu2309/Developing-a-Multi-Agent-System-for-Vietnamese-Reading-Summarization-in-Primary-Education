package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.MasState;

@Repository
public interface MasStateRepository extends JpaRepository<MasState, String> {
    List<MasState> findBySessionSessionId(String sessionId);
    Optional<MasState> findFirstBySessionSessionIdOrderByCreatedAtDesc(String sessionId);
    Optional<MasState> findByStateIdAndSessionSessionId(String stateId, String sessionId);
}
