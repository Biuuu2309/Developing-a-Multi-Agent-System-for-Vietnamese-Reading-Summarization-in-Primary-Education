package com.example.my_be.service;

import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.model.MasPlan;
import com.example.my_be.model.MasState;
import com.example.my_be.repository.MasPlanRepository;
import com.example.my_be.repository.MasStateRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MasPlanService {
    @Autowired
    private MasPlanRepository masPlanRepository;

    @Autowired
    private MasStateRepository masStateRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public MasPlan createFromState(String stateId, String intentJson, String planJson) {
        MasState state = masStateRepository.findById(stateId)
            .orElseThrow(() -> new RuntimeException("MasState not found: " + stateId));

        MasPlan plan = new MasPlan();
        plan.setPlanId(UUID.randomUUID().toString());
        plan.setState(state);
        plan.setIntent(intentJson);

        try {
            JsonNode planNode = objectMapper.readTree(planJson != null ? planJson : "{}");
            // pipeline: danh sách bước thực thi
            JsonNode pipelineNode = planNode.path("pipeline");
            plan.setPipeline(pipelineNode.isMissingNode() ? "[]" : pipelineNode.toString());
            // context: lưu toàn bộ plan để sau này có thể phân tích lại
            plan.setContext(planNode.toString());
        } catch (Exception e) {
            // Nếu parse lỗi, vẫn lưu raw JSON để không mất dữ liệu
            plan.setPipeline("[]");
            plan.setContext(planJson);
        }

        return masPlanRepository.save(plan);
    }
}

