package com.example.my_be.service;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.dto.SummaryDTO;
import com.example.my_be.model.ReadHistory;
import com.example.my_be.model.Summary;
import com.example.my_be.model.User;
import com.example.my_be.repository.ReadHistoryRepository;
import com.example.my_be.repository.SummaryRepository;

@Service
public class SummaryService {

    @Autowired
    private SummaryRepository summaryRepository;

    @Autowired
    private ReadHistoryRepository readHistoryRepository;

    @Autowired
    private UserService userService;

    public void logReadHistory(User user, Summary summary) {
        ReadHistory readHistory = new ReadHistory();
        readHistory.setUser(user);
        readHistory.setSummary(summary);
        readHistoryRepository.save(readHistory);
    }

    public Summary createSummary(Summary summary) {
        return summaryRepository.save(summary);
    }

    public void deleteSummary(String id) {
        summaryRepository.deleteById(id);
    }

    public List<SummaryDTO> getAllSummaries() {
        List<Summary> summaries = summaryRepository.findByStatus("APPROVED"); // Only APPROVED
        List<SummaryDTO> summaryDTOs = new ArrayList<>();
        for (Summary summary : summaries) {
            SummaryDTO dto = new SummaryDTO();
            dto.setSummaryId(summary.getSummaryId());
            dto.setTitle(summary.getTitle());
            dto.setContent(summary.getContent());
            dto.setSummaryContent(summary.getSummaryContent());
            dto.setStatus(summary.getStatus());
            dto.setMethod(summary.getMethod());
            dto.setGrade(summary.getGrade());
            dto.setReadCount(summary.getReadCount());
            dto.setCreatedByUserId(summary.getCreatedBy().getUserId());
            dto.setCreatedAt(summary.getCreatedAt());
            dto.setApprovedAt(summary.getApprovedAt());
            dto.setImageUrl(summary.getImageUrl());
            summaryDTOs.add(dto);
        }
        return summaryDTOs;
    }

    public Optional<Summary> getSummaryById(String id) {
        Optional<Summary> summary = summaryRepository.findById(id);
        return summary.filter(s -> "APPROVED".equals(s.getStatus())); // Only return if APPROVED
    }

    public Optional<Summary> getSummaryByIdwoStatus(String id) {
        Optional<Summary> summary = summaryRepository.getSummaryByIdwoStatus(id);
        // Return summary with the Id not filter anything
        return summary; // No filter, used by admin
        
    }

    public List<Summary> getAllSummariesEntities() {
        return summaryRepository.findAll(); // Unchanged for admin
    }

    public void updateSummaryStatus(String id, String status) {
        Optional<Summary> optionalSummary = summaryRepository.findById(id); // Use raw findById here
        if (optionalSummary.isPresent()) {
            Summary summary = optionalSummary.get();
            summary.setStatus(status);
            summaryRepository.save(summary);
        }
    }

    public List<Summary> getSummariesByStatus(String status) {
        return summaryRepository.findByStatus(status); // No filter, used by status endpoint
    }

    public List<SummaryDTO> getSummariesByContributor(String userId) {
        Optional<User> optionalUser = userService.getUserById(userId);
        if (optionalUser.isPresent()) {
            List<Summary> summaries = summaryRepository.findByCreatedBy(optionalUser.get()); // All statuses
            List<SummaryDTO> summaryDTOs = new ArrayList<>();
            for (Summary summary : summaries) {
                SummaryDTO dto = new SummaryDTO();
                dto.setSummaryId(summary.getSummaryId());
                dto.setTitle(summary.getTitle());
                dto.setContent(summary.getContent());
                dto.setSummaryContent(summary.getSummaryContent());
                dto.setStatus(summary.getStatus());
                dto.setMethod(summary.getMethod());
                dto.setGrade(summary.getGrade());
                dto.setCreatedAt(summary.getCreatedAt());
                dto.setApprovedAt(summary.getApprovedAt());
                dto.setCreatedByUserId(summary.getCreatedBy().getUserId());
                summaryDTOs.add(dto);
            }
            return summaryDTOs;
        } else {
            return new ArrayList<>();
        }
    }

    public List<Summary> searchSummariesByTitleAndGrade(String searchTerm, String grade) {
        return summaryRepository.findByTitleContainingIgnoreCaseAndGrade(searchTerm, grade).stream()
            .filter(summary -> "APPROVED".equals(summary.getStatus()))
            .collect(Collectors.toList());
    }

    public Summary updateSummary(Summary summary) {
        return summaryRepository.save(summary);
    }

    public List<Summary> searchSummaries(String searchTerm, String status, String method, String grade) {
        return summaryRepository.findByTitleContainingOrContentContainingOrStatusContainingOrMethodContainingOrGradeContaining(
            searchTerm, searchTerm, status, method, grade
        ).stream()
            .filter(summary -> "APPROVED".equals(summary.getStatus()))
            .collect(Collectors.toList());
    }

    public List<Summary> getTop10MostReadSummaries() {
        return summaryRepository.findTop10ByOrderByReadCountDesc().stream()
            .filter(summary -> "APPROVED".equals(summary.getStatus()))
            .collect(Collectors.toList());
    }

    public List<SummaryDTO> getSummariesByGrade(String grade) {
        List<Summary> summaries = summaryRepository.findByGrade(grade).stream()
            .filter(summary -> "APPROVED".equals(summary.getStatus()))
            .collect(Collectors.toList());
        List<SummaryDTO> summaryDTOs = new ArrayList<>();
        for (Summary summary : summaries) {
            SummaryDTO dto = new SummaryDTO();
            dto.setSummaryId(summary.getSummaryId());
            dto.setTitle(summary.getTitle());
            dto.setContent(summary.getContent());
            dto.setSummaryContent(summary.getSummaryContent());
            dto.setStatus(summary.getStatus());
            dto.setMethod(summary.getMethod());
            dto.setGrade(summary.getGrade());
            dto.setImageUrl(summary.getImageUrl());
            dto.setCreatedAt(summary.getCreatedAt());
            dto.setApprovedAt(summary.getApprovedAt());
            dto.setCreatedByUserId(summary.getCreatedBy().getUserId());
            summaryDTOs.add(dto);
        }
        return summaryDTOs;
    }

    public List<Summary> searchSummariesByTitle(String searchTerm) {
        return summaryRepository.findByTitleContainingIgnoreCase(searchTerm).stream()
            .filter(summary -> "APPROVED".equals(summary.getStatus()))
            .collect(Collectors.toList());
    }

    public List<Summary> getSummariesByMethod(String method) {
        return summaryRepository.findByMethod(method).stream()
            .filter(summary -> "APPROVED".equals(summary.getStatus()))
            .collect(Collectors.toList());
    }
}
