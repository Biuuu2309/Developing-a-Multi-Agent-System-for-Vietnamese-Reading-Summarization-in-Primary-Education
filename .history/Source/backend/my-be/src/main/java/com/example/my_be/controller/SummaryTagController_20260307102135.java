package com.example.my_be.controller;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

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

import com.example.my_be.model.Summary;
import com.example.my_be.model.SummaryTag;
import com.example.my_be.model.Tag;
import com.example.my_be.service.SummaryService;
import com.example.my_be.service.SummaryTagService;
import com.example.my_be.service.TagService;

@RestController
@RequestMapping("/api/summary-tags")
public class SummaryTagController {

    // DTO for SummaryTag response
    public static class SummaryTagDTO {
        private String summaryTagId;
        private String summaryId;
        private String summaryTitle;
        private String tagId;
        private String tagName;

        // Constructors
        public SummaryTagDTO() {}

        public SummaryTagDTO(String summaryTagId, String summaryId, String summaryTitle, String tagId, String tagName) {
            this.summaryTagId = summaryTagId;
            this.summaryId = summaryId;
            this.summaryTitle = summaryTitle;
            this.tagId = tagId;
            this.tagName = tagName;
        }

        // Getters and Setters
        public String getSummaryTagId() { return summaryTagId; }
        public void setSummaryTagId(String summaryTagId) { this.summaryTagId = summaryTagId; }
        
        public String getSummaryId() { return summaryId; }
        public void setSummaryId(String summaryId) { this.summaryId = summaryId; }
        
        public String getSummaryTitle() { return summaryTitle; }
        public void setSummaryTitle(String summaryTitle) { this.summaryTitle = summaryTitle; }
        
        public String getTagId() { return tagId; }
        public void setTagId(String tagId) { this.tagId = tagId; }
        
        public String getTagName() { return tagName; }
        public void setTagName(String tagName) { this.tagName = tagName; }
    }

    @Autowired
    private SummaryTagService summaryTagService;

    @Autowired
    private SummaryService summaryService;

    @Autowired
    private TagService tagService;

    // Get all tags for a specific summary
    @GetMapping("/summary/{summaryId}")
    public ResponseEntity<List<SummaryTagDTO>> getTagsBySummary(@PathVariable String summaryId) {
        Optional<Summary> summary = summaryService.getSummaryByIdwoStatus(summaryId);
        if (summary.isPresent()) {
            List<SummaryTag> tags = summaryTagService.getTagsBySummary(summary.get());
            List<SummaryTagDTO> tagDTOs = tags.stream()
                .map(tag -> new SummaryTagDTO(
                    tag.getSummaryTagId(),
                    tag.getSummary().getSummaryId(),
                    tag.getSummary().getTitle(),
                    tag.getTag().getTagId(),
                    tag.getTag().getName()
                ))
                .collect(Collectors.toList());
            return new ResponseEntity<>(tagDTOs, HttpStatus.OK);
        }
        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    // Get all summaries associated with a specific tag
    @GetMapping("/tag/{tagId}")
    public ResponseEntity<List<SummaryTagDTO>> getSummariesByTag(@PathVariable String tagId) {
        Optional<Tag> tag = tagService.getTagById(tagId);
        if (tag.isPresent()) {
            List<SummaryTag> summaries = summaryTagService.getSummariesByTag(tag.get());
            List<SummaryTagDTO> summaryDTOs = summaries.stream()
                .map(summary -> new SummaryTagDTO(
                    summary.getSummaryTagId(),
                    summary.getSummary().getSummaryId(),
                    summary.getSummary().getTitle(),
                    summary.getTag().getTagId(),
                    summary.getTag().getName()
                ))
                .collect(Collectors.toList());
            return new ResponseEntity<>(summaryDTOs, HttpStatus.OK);
        }
        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    // Create a new association between a summary and a tag
    @PostMapping
    public ResponseEntity<SummaryTag> createSummaryTag(@RequestBody Map<String, String> request) {
        String summaryId = request.get("summaryId");
        String tagId = request.get("tagId");
        
        // Fetch the summary and tag by their IDs
        Optional<Summary> summaryOpt = summaryService.getSummaryByIdwoStatus(summaryId);
        Optional<Tag> tagOpt = tagService.getTagById(tagId);
        
        if (summaryOpt.isEmpty() || tagOpt.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        
        // Create the association
        SummaryTag summaryTag = new SummaryTag();
        summaryTag.setSummary(summaryOpt.get());
        summaryTag.setTag(tagOpt.get());
        
        SummaryTag createdAssociation = summaryTagService.createSummaryTag(summaryTag);
        return new ResponseEntity<>(createdAssociation, HttpStatus.CREATED);
    }

    // Delete an association between a summary and a tag by ID
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteSummaryAssociation(@PathVariable String id) {
        Optional<SummaryTag> existingAssociation = summaryTagService.getSummaryTagById(id);
        if (existingAssociation.isPresent()) {
            summaryTagService.deleteSummaryTag(id);
            return new ResponseEntity<>(HttpStatus.NO_CONTENT);
        }
        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }
}
