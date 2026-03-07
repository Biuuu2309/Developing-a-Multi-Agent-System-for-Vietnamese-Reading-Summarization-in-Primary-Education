package com.example.my_be.model;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "mas_agent_memories")
@Data
@NoArgsConstructor
public class MasAgentMemory {
    @Id
    @Column(name = "memory_id")
    private String memoryId;

    @ManyToOne
    @JoinColumn(name = "agent_id", nullable = false)
    private Agent agent;

    @Column(name = "task_type", length = 100)
    private String taskType;

    @Column(name = "input_data", columnDefinition = "JSON")
    private String inputData;

    @Column(name = "output_data", columnDefinition = "TEXT")
    private String outputData;

    @Column(name = "success")
    private Boolean success = true;

    @Column(name = "context", columnDefinition = "JSON")
    private String context;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
