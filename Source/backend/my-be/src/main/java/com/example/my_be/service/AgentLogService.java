package com.example.my_be.service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.dto.CreateAgentLogRequest;
import com.example.my_be.model.AgentLog;
import com.example.my_be.model.AgentLog.LogStatus;
import com.example.my_be.repository.AgentLogRepository;

@Service
public class AgentLogService {
    @Autowired
    private AgentLogRepository agentLogRepository;

    public AgentLog createAgentLog(CreateAgentLogRequest request) {
        AgentLog log = new AgentLog();
        log.setLogId(UUID.randomUUID().toString());
        log.setMessageId(request.getMessageId());
        log.setAgentId(request.getAgentId());
        log.setInput(request.getInput());
        log.setOutput(request.getOutput());
        log.setDurationMs(request.getDurationMs());
        log.setStatus(LogStatus.valueOf(request.getStatus().toUpperCase()));
        
        return agentLogRepository.save(log);
    }

    public List<AgentLog> getLogsByMessageId(String messageId) {
        return agentLogRepository.findByMessageId(messageId);
    }

    public List<AgentLog> getLogsByAgentId(String agentId) {
        return agentLogRepository.findByAgentId(agentId);
    }

    public Optional<AgentLog> getLogById(String logId) {
        return agentLogRepository.findById(logId);
    }
}

