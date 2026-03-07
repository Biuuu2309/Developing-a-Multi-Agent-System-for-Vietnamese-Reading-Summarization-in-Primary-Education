package com.example.my_be.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.my_be.dto.MasChatRequest;
import com.example.my_be.dto.MasChatResponse;
import com.example.my_be.dto.MasSessionRequest;
import com.example.my_be.dto.MasSessionResponse;
import com.example.my_be.dto.MasStateResponse;
import com.example.my_be.model.Agent;
import com.example.my_be.model.AgentLog;
import com.example.my_be.model.MasSession;
import com.example.my_be.service.AgentLogService;
import com.example.my_be.service.AgentService;
import com.example.my_be.service.MasSessionService;
import com.example.my_be.service.MasSystemService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;

@RestController
@RequestMapping("/api/mas")
@Tag(name = "MAS System", description = "Multi-Agent System API")
public class MASSystemController {
    @Autowired
    private MasSystemService masSystemService;

    @Autowired
    private MasSessionService masSessionService;

    @Autowired
    private AgentService agentService;

    @Autowired
    private AgentLogService agentLogService;

    @PostMapping("/chat")
    @Operation(summary = "Process chat message through MAS")
    public ResponseEntity<MasChatResponse> chat(@RequestBody MasChatRequest request) {
        MasChatResponse response = masSystemService.processChat(request);
        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    @PostMapping("/sessions")
    @Operation(summary = "Create new MAS session")
    public ResponseEntity<MasSessionResponse> createSession(@RequestBody MasSessionRequest request) {
        MasSessionResponse response = masSessionService.createSession(request);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    @GetMapping("/sessions/user/{userId}")
    @Operation(summary = "Get all sessions for a user")
    public ResponseEntity<List<MasSessionResponse>> getSessionsByUserId(@PathVariable String userId) {
        List<MasSessionResponse> sessions = masSessionService.getSessionsByUserId(userId);
        return new ResponseEntity<>(sessions, HttpStatus.OK);
    }

    @GetMapping("/sessions/{sessionId}")
    @Operation(summary = "Get session by ID")
    public ResponseEntity<MasSessionResponse> getSession(
            @PathVariable String sessionId,
            @RequestParam String userId) {
        return masSessionService.getSessionById(sessionId, userId)
            .map(body -> new ResponseEntity<>(body, HttpStatus.OK))
            .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    @PutMapping("/sessions/{sessionId}/status")
    @Operation(summary = "Update session status")
    public ResponseEntity<MasSessionResponse> updateSessionStatus(
            @PathVariable String sessionId,
            @RequestParam MasSession.SessionStatus status) {
        MasSessionResponse response = masSessionService.updateSessionStatus(sessionId, status);
        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    @GetMapping("/sessions/{sessionId}/history")
    @Operation(summary = "Get session history (states)")
    public ResponseEntity<List<MasStateResponse>> getSessionHistory(
            @PathVariable String sessionId,
            @RequestParam String userId) {
        List<MasStateResponse> history = masSystemService.getSessionHistory(sessionId, userId);
        return new ResponseEntity<>(history, HttpStatus.OK);
    }

    @GetMapping("/sessions/{sessionId}/latest-state")
    @Operation(summary = "Get latest state for a session")
    public ResponseEntity<MasStateResponse> getLatestState(
            @PathVariable String sessionId,
            @RequestParam String userId) {
        return masSystemService.getLatestState(sessionId, userId)
            .map(body -> new ResponseEntity<>(body, HttpStatus.OK))
            .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    @PostMapping("/agents")
    @Operation(summary = "Create new agent")
    public ResponseEntity<Agent> createAgent(@RequestBody Agent agent) {
        return new ResponseEntity<>(agentService.createAgent(agent), HttpStatus.CREATED);
    }

    @GetMapping("/agents")
    @Operation(summary = "Get all agents")
    public ResponseEntity<List<Agent>> getAllAgents() {
        return new ResponseEntity<>(agentService.getAllAgents(), HttpStatus.OK);
    }

    @GetMapping("/agents/{agentId}")
    @Operation(summary = "Get agent by ID")
    public ResponseEntity<Agent> getAgentById(@PathVariable String agentId) {
        return agentService.getAgentById(agentId)
            .map(body -> new ResponseEntity<>(body, HttpStatus.OK))
            .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    @DeleteMapping("/agents/{agentId}")
    @Operation(summary = "Delete agent")
    public ResponseEntity<Void> deleteAgent(@PathVariable String agentId) {
        agentService.deleteAgent(agentId);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @GetMapping("/agent-logs/message/{messageId}")
    @Operation(summary = "Get logs by message ID")
    public ResponseEntity<List<AgentLog>> getLogsByMessageId(@PathVariable String messageId) {
        return new ResponseEntity<>(agentLogService.getLogsByMessageId(messageId), HttpStatus.OK);
    }

    @GetMapping("/agent-logs/agent/{agentId}")
    @Operation(summary = "Get logs by agent ID")
    public ResponseEntity<List<AgentLog>> getLogsByAgentId(@PathVariable String agentId) {
        return new ResponseEntity<>(agentLogService.getLogsByAgentId(agentId), HttpStatus.OK);
    }

    @GetMapping("/agent-logs/{logId}")
    @Operation(summary = "Get log by ID")
    public ResponseEntity<AgentLog> getLogById(@PathVariable String logId) {
        return agentLogService.getLogById(logId)
            .map(body -> new ResponseEntity<>(body, HttpStatus.OK))
            .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
}
