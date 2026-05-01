package com.example.my_be.service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.dto.SummaryDifficultyAdjustmentDTO;
import com.example.my_be.model.Summary;
import com.example.my_be.model.SummaryDifficultyAdjustment;
import com.example.my_be.model.User;
import com.example.my_be.repository.SummaryDifficultyAdjustmentRepository;
import com.example.my_be.repository.SummaryRepository;
import com.example.my_be.repository.UserRepository;

@Service
public class SummaryDifficultyAdjustmentService {

    @Autowired
    private SummaryDifficultyAdjustmentRepository summaryDifficultyAdjustmentRepository;

    @Autowired
    private SummaryRepository summaryRepository;

    @Autowired
    private UserRepository userRepository;

    public Optional<SummaryDifficultyAdjustmentDTO> getById(Long id) {
        return summaryDifficultyAdjustmentRepository.findById(id).map(this::mapToDTO);
    }

    public List<SummaryDifficultyAdjustmentDTO> getBySummaryId(String summaryId) {
        return summaryDifficultyAdjustmentRepository.findBySummaryIdRefOrderByCreatedAtDesc(summaryId).stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    public List<SummaryDifficultyAdjustmentDTO> getByUserId(String userId) {
        return summaryDifficultyAdjustmentRepository.findByCreatedByUserIdRefOrderByCreatedAtDesc(userId).stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    public SummaryDifficultyAdjustmentDTO create(SummaryDifficultyAdjustmentDTO dto) {
        Summary summary = summaryRepository.findById(dto.getSummaryId())
                .orElseThrow(() -> new RuntimeException("Summary not found"));
        User user = userRepository.findById(dto.getCreatedByUserId())
                .orElseThrow(() -> new RuntimeException("User not found"));

        SummaryDifficultyAdjustment entity = new SummaryDifficultyAdjustment();
        entity.setSummary(summary);
        entity.setCreatedBy(user);
        entity.setContentSummary(dto.getContentSummary());
        entity.setSummaryIncrease(dto.getSummaryIncrease());
        entity.setSummaryDecrease(dto.getSummaryDecrease());

        SummaryDifficultyAdjustment saved = summaryDifficultyAdjustmentRepository.save(entity);
        return mapToDTO(saved);
    }

    public void delete(Long id) {
        summaryDifficultyAdjustmentRepository.deleteById(id);
    }

    public SummaryDifficultyAdjustmentDTO mapToDTO(SummaryDifficultyAdjustment entity) {
        SummaryDifficultyAdjustmentDTO dto = new SummaryDifficultyAdjustmentDTO();
        dto.setId(entity.getId());
        dto.setCreatedAt(entity.getCreatedAt());
        dto.setContentSummary(entity.getContentSummary());
        dto.setSummaryIncrease(entity.getSummaryIncrease());
        dto.setSummaryDecrease(entity.getSummaryDecrease());
        dto.setSummaryId(entity.getSummaryIdRef());
        dto.setCreatedByUserId(entity.getCreatedByUserIdRef());
        return dto;
    }
}
