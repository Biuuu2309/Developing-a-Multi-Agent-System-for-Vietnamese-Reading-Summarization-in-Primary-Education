package com.example.my_be.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.my_be.dto.CreateAgentLogRequest;
import com.example.my_be.model.AgentLog;
import com.example.my_be.service.AgentLogService;

@RestController
@RequestMapping("/api/agent_log")
public class AgentLogController {
    @Autowired
    private AgentLogService agentLogService;

    @PostMapping
    public ResponseEntity<AgentLog> createAgentLog(@RequestBody CreateAgentLogRequest request) {
        return new ResponseEntity<>(agentLogService.createAgentLog(request), HttpStatus.CREATED);
    }

    @GetMapping("/message/{messageId}")
    public ResponseEntity<List<AgentLog>> getLogsByMessageId(@PathVariable String messageId) {
        return new ResponseEntity<>(agentLogService.getLogsByMessageId(messageId), HttpStatus.OK);
    }

     @GetMapping("/agent/{agentId}")
    public ResponseEntity<List<AgentLog>> getLogsByAgentId(@PathVariable String agentId) {
        return new ResponseEntity<>(agentLogService.getLogsByAgentId(agentId), HttpStatus.OK);
    }

    @GetMapping("/{logId}")
    public ResponseEntity<AgentLog> getLogById(@PathVariable String logId) {
        return agentLogService.getLogById(logId)
            .map(body -> new ResponseEntity<>(body, HttpStatus.OK))
            .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
}

