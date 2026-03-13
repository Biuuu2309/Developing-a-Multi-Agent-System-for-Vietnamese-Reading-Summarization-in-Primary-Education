package com.example.my_be.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.my_be.model.MasPlan;

@Repository
public interface MasPlanRepository extends JpaRepository<MasPlan, String> {
    List<MasPlan> findByStateStateId(String stateId);
    Optional<MasPlan> findFirstByStateStateIdOrderByCreatedAtDesc(String stateId);
}
