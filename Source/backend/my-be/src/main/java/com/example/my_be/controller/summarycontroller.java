package com.example.my_be.controller;

import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import org.hibernate.Hibernate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.my_be.dto.SummaryDTO;
import com.example.my_be.model.Summary;
import com.example.my_be.model.User;
import com.example.my_be.repository.UserRepository;
import com.example.my_be.service.SummaryService;

@RestController
@RequestMapping("/api/summaries")
public class SummaryController {

    @Autowired
    private SummaryService summaryService;

    @Autowired
    private UserRepository userRepository; // To handle user retrieval by ID

    // Get all summaries
@GetMapping
public ResponseEntity<List<SummaryDTO>> getAllSummaries() {
    List<SummaryDTO> summaries = summaryService.getAllSummaries();
    return new ResponseEntity<>(summaries, HttpStatus.OK);
}


@GetMapping("/{id}")
public ResponseEntity<SummaryDTO> getSummaryById(@PathVariable String id, @RequestParam(required = false) String userId) {
    Optional<Summary> summaryOpt = summaryService.getSummaryById(id);

    if (summaryOpt.isPresent()) {
        Summary summary = summaryOpt.get();

        // Log the read history with the userId (no need to fetch User object)
        User user = userRepository.findById(userId).orElse(null); // Fetch the user using userId
        if (user != null) {
            summaryService.logReadHistory(user, summary); // Log the read history
        }

        // Increment the read count
        summary.setReadCount(summary.getReadCount() + 1);
        summaryService.updateSummary(summary);

        // Map the Summary entity to SummaryDTO
        SummaryDTO summaryDTO = mapToSummaryDTO(summary);
        return new ResponseEntity<>(summaryDTO, HttpStatus.OK);
    } else {
        return new ResponseEntity<>(HttpStatus.NOT_FOUND); // If the summary is not found
    }
}


@GetMapping("/top10")
public ResponseEntity<List<SummaryDTO>> getTop10MostReadSummaries() {
    List<Summary> topSummaries = summaryService.getTop10MostReadSummaries();
    
    // Map the entities to DTOs
    List<SummaryDTO> topSummaryDTOs = topSummaries.stream()
        .map(this::mapToSummaryDTO)
        .collect(Collectors.toList());
        
    return new ResponseEntity<>(topSummaryDTOs, HttpStatus.OK);
}



@GetMapping("/search")
public ResponseEntity<List<SummaryDTO>> searchSummariesByTitleAndGrade(
    @RequestParam String searchTerm, @RequestParam(required = false) String grade) {
  List<Summary> summaries;
  if (grade != null && !grade.isEmpty()) {
    summaries = summaryService.searchSummariesByTitleAndGrade(searchTerm, grade);
  } else {
    summaries = summaryService.searchSummariesByTitle(searchTerm);
  }
  List<SummaryDTO> summaryDTOs = summaries.stream()
      .map(this::mapToSummaryDTO)
      .collect(Collectors.toList());
  return new ResponseEntity<>(summaryDTOs, HttpStatus.OK);
}

public class SummaryAdminDTO {
    private String summaryId;
    private String title;
    private String status;
    private String method;
    private String grade;
    private int readCount;
    private String createdByUserId;
    private String createdByUserName; // Optional: include user name for display
    private Date createdAt;
    private Date approvedAt;

    // Getters
    public String getSummaryId() {
        return summaryId;
    }

    public String getTitle() {
        return title;
    }

    public String getStatus() {
        return status;
    }

    public String getMethod() {
        return method;
    }

    public String getGrade() {
        return grade;
    }

    public int getReadCount() {
        return readCount;
    }

    public String getCreatedByUserId() {
        return createdByUserId;
    }

    public String getCreatedByUserName() {
        return createdByUserName;
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public Date getApprovedAt() {
        return approvedAt;
    }

    // Setters
    public void setSummaryId(String summaryId) {
        this.summaryId = summaryId;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public void setMethod(String method) {
        this.method = method;
    }

    public void setGrade(String grade) {
        this.grade = grade;
    }

    public void setReadCount(int readCount) {
        this.readCount = readCount;
    }

    public void setCreatedByUserId(String createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

    public void setCreatedByUserName(String createdByUserName) {
        this.createdByUserName = createdByUserName;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }

    public void setApprovedAt(Date approvedAt) {
        this.approvedAt = approvedAt;
    }
}

private SummaryDTO mapToSummaryDTO(Summary summary) {
    SummaryDTO summaryDTO = new SummaryDTO();
    summaryDTO.setSummaryId(summary.getSummaryId());
    summaryDTO.setTitle(summary.getTitle());
    summaryDTO.setContent(summary.getContent());
    summaryDTO.setSummaryContent(summary.getSummaryContent());
    summaryDTO.setStatus(summary.getStatus());
    summaryDTO.setMethod(summary.getMethod());
    summaryDTO.setGrade(summary.getGrade());
    summaryDTO.setReadCount(summary.getReadCount());
    summaryDTO.setCreatedByUserId(summary.getCreatedBy().getUserId());
    summaryDTO.setImageUrl(summary.getImageUrl()); // Assuming you're using a User object for createdBy

    // Add createdAt and approvedAt
    summaryDTO.setCreatedAt(summary.getCreatedAt());
    summaryDTO.setApprovedAt(summary.getApprovedAt());

    return summaryDTO;
}

@GetMapping("/admin")
public ResponseEntity<List<SummaryAdminDTO>> getSummariesForAdmin() {
    List<Summary> summaries = summaryService.getAllSummariesEntities();
    
    List<SummaryAdminDTO> adminDTOs = summaries.stream()
        .map(this::mapToSummaryAdminDTO)
        .collect(Collectors.toList());
        
    return new ResponseEntity<>(adminDTOs, HttpStatus.OK);
}

private SummaryAdminDTO mapToSummaryAdminDTO(Summary summary) {
    SummaryAdminDTO adminDTO = new SummaryAdminDTO();
    adminDTO.setSummaryId(summary.getSummaryId());
    adminDTO.setTitle(summary.getTitle());
    adminDTO.setStatus(summary.getStatus());
    adminDTO.setMethod(summary.getMethod());
    adminDTO.setGrade(summary.getGrade());
    adminDTO.setReadCount(summary.getReadCount());
    adminDTO.setCreatedByUserId(summary.getCreatedBy().getUserId());
    adminDTO.setCreatedByUserName(summary.getCreatedBy().getFullName()); // If you want to include user name
    adminDTO.setCreatedAt(summary.getCreatedAt());
    adminDTO.setApprovedAt(summary.getApprovedAt());
    
    return adminDTO;
}

@PostMapping
public ResponseEntity<Summary> createSummary(@RequestBody Summary summary) {
    // Manually set createdAt if it's not already set
    if (summary.getCreatedAt() == null) {
        summary.setCreatedAt(new Date()); // Set the current date and time as createdAt
    }

    // Handle approval time if necessary
    if ("APPROVED".equals(summary.getStatus())) {
        summary.setApprovedAt(new Date()); // Set the approval time when the status is APPROVED
    }

    Optional<User> user = userRepository.findById(summary.getCreatedBy().getUserId());
    if (user.isPresent()) {
        summary.setCreatedBy(user.get()); // Set the user for the summary
        Summary createdSummary = summaryService.createSummary(summary);
        return new ResponseEntity<>(createdSummary, HttpStatus.CREATED);
    } else {
        return new ResponseEntity<>(HttpStatus.NOT_FOUND); // If the user does not exist
    }
}

    

@PatchMapping("/{id}")  // Use PATCH instead of PUT
public ResponseEntity<Object> patchSummary(
    @PathVariable String id,
    @RequestBody Map<String, Object> updates  // Accept partial fields
) {
    Optional<Summary> existingSummary = summaryService.getSummaryByIdwoStatus(id);
    if (existingSummary.isPresent()) {
        Summary summary = existingSummary.get();
         Hibernate.initialize(summary);
        updates.forEach((key, value) -> {
            switch (key) {
                case "status": summary.setStatus((String) value); break;
                case "title": summary.setTitle((String) value); break;
                // Add other fields as needed
            }
        });
        Summary updatedSummary = summaryService.updateSummary(summary);
        return ResponseEntity.ok(updatedSummary);
    } else {
        return ResponseEntity.notFound().build();
    }
}
    // Delete a summary
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteSummary(@PathVariable String id) {
        summaryService.deleteSummary(id);
        //print the console
        
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
// New bulk delete endpoint
@DeleteMapping("/bulk")
public ResponseEntity<Void> deleteSummaries(@RequestBody List<String> ids) {
    try {
        ids.forEach(id -> {
            summaryService.deleteSummary(id);
            System.out.println("Deleted summary with ID: " + id);
        });
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    } catch (Exception e) {
        System.err.println("Error deleting summaries: " + e.getMessage());
        return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
    // Get all summaries by status (e.g., PENDING, APPROVED)
    @GetMapping("/status/{status}")
    public ResponseEntity<List<SummaryDTO>> getSummariesByStatus(@PathVariable String status) {
        List<Summary> summaries = summaryService.getSummariesByStatus(status);
        List<SummaryDTO> summaryDTOs = summaries.stream()
            .map(this::mapToSummaryDTO)
            .collect(Collectors.toList());
        return new ResponseEntity<>(summaryDTOs, HttpStatus.OK);
    }

    // Get all summaries created by a specific user
    @GetMapping("/contributor/{userId}")
    public ResponseEntity<List<SummaryDTO>> getSummariesByContributor(@PathVariable String userId) {
        List<SummaryDTO> summaries = summaryService.getSummariesByContributor(userId);
        return new ResponseEntity<>(summaries, HttpStatus.OK);
    }
    // Approve or reject a summary
    @PutMapping("/{id}/status")
    public ResponseEntity<Void> updateSummaryStatus(@PathVariable String id, @RequestBody Map<String, String> request) {
        String status = request.get("status");
        summaryService.updateSummaryStatus(id, status);
        return new ResponseEntity<>(HttpStatus.OK);
    }

   
     // Get all summaries by grade
     @GetMapping("/grade/{grade}")
     public ResponseEntity<List<SummaryDTO>> getSummariesByGrade(@PathVariable String grade) {
         List<SummaryDTO> summaries = summaryService.getSummariesByGrade(grade);
         return new ResponseEntity<>(summaries, HttpStatus.OK);
     }

    // Get all summaries by method (e.g., extractive, abstractive)
    @GetMapping("/method/{method}")
    public ResponseEntity<List<SummaryDTO>> getSummariesByMethod(@PathVariable String method) {
        List<Summary> summaries = summaryService.getSummariesByMethod(method);
        List<SummaryDTO> summaryDTOs = summaries.stream()
            .map(this::mapToSummaryDTO)
            .collect(Collectors.toList());
        return new ResponseEntity<>(summaryDTOs, HttpStatus.OK);
    }

    // Debug endpoint to check all grades in database
    @GetMapping("/debug/grades")
    public ResponseEntity<List<String>> getAllGrades() {
        List<Summary> allSummaries = summaryService.getAllSummariesEntities();
        List<String> grades = allSummaries.stream()
            .map(Summary::getGrade)
            .distinct()
            .collect(Collectors.toList());
        return new ResponseEntity<>(grades, HttpStatus.OK);
    }
}
