package com.example.my_be.service;

import java.math.BigDecimal;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.my_be.model.MasEvaluation;
import com.example.my_be.model.MasState;
import com.example.my_be.repository.MasEvaluationRepository;
import com.example.my_be.repository.MasStateRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MasEvaluationService {
    @Autowired
    private MasEvaluationRepository masEvaluationRepository;

    @Autowired
    private MasStateRepository masStateRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public MasEvaluation createFromState(String stateId, String evaluationJson) {
        MasState state = masStateRepository.findById(stateId)
            .orElseThrow(() -> new RuntimeException("MasState not found: " + stateId));

        MasEvaluation evaluation = new MasEvaluation();
        evaluation.setEvaluationId(UUID.randomUUID().toString());
        evaluation.setState(state);

        try {
            JsonNode evalNode = objectMapper.readTree(evaluationJson != null ? evaluationJson : "{}");
            evaluation.setMetrics(evalNode.toString());

            // Map các metric thường dùng nếu có
            double rouge1F1 = evalNode.path("rouge1_f1").asDouble(Double.NaN);
            double rougeLF1 = evalNode.path("rougeL_f1").asDouble(Double.NaN);
            double bertF1 = evalNode.path("bertscore_f1").asDouble(Double.NaN);

            if (!Double.isNaN(rouge1F1)) {
                evaluation.setRouge1F1(BigDecimal.valueOf(rouge1F1));
            }
            if (!Double.isNaN(rougeLF1)) {
                evaluation.setRougeLF1(BigDecimal.valueOf(rougeLF1));
            }
            if (!Double.isNaN(bertF1)) {
                evaluation.setBertscoreF1(BigDecimal.valueOf(bertF1));
            }

            if (evalNode.has("comment")) {
                evaluation.setComment(evalNode.path("comment").asText());
            }

            // Map thêm các text difficulty features nếu có
            if (evalNode.has("difficulty_level")) {
                evaluation.setDifficultyLevel(evalNode.path("difficulty_level").asText(null));
            }

            evaluation.setTotalWords(asInteger(evalNode, "total_words"));
            evaluation.setUniqueWords(asInteger(evalNode, "unique_words"));
            evaluation.setTypeTokenRatio(asBigDecimal(evalNode, "type_token_ratio"));
            evaluation.setRareWordRatio(asBigDecimal(evalNode, "rare_word_ratio"));
            evaluation.setUnknownWordRatio(asBigDecimal(evalNode, "unknown_word_ratio"));
            evaluation.setAvgWordGrade(asBigDecimal(evalNode, "avg_word_grade"));
            evaluation.setNumSentences(asInteger(evalNode, "num_sentences"));
            evaluation.setAvgSentenceLength(asBigDecimal(evalNode, "avg_sentence_length"));
            evaluation.setMaxSentenceLength(asInteger(evalNode, "max_sentence_length"));
            evaluation.setMinSentenceLength(asInteger(evalNode, "min_sentence_length"));
            evaluation.setLongSentenceRatio(asBigDecimal(evalNode, "long_sentence_ratio"));
            evaluation.setAvgWordLength(asBigDecimal(evalNode, "avg_word_length"));
            evaluation.setWordsPerSentence(asBigDecimal(evalNode, "words_per_sentence"));
            evaluation.setLexicalDensity(asBigDecimal(evalNode, "lexical_density"));

            if (evalNode.has("matched_rules")) {
                evaluation.setMatchedRules(evalNode.path("matched_rules").asText());
            }
        } catch (Exception e) {
            // Nếu parse lỗi, vẫn lưu raw JSON để không mất dữ liệu
            evaluation.setMetrics(evaluationJson);
        }

        return masEvaluationRepository.save(evaluation);
    }

    private Integer asInteger(JsonNode node, String field) {
        if (node.has(field) && node.path(field).canConvertToInt()) {
            return node.path(field).asInt();
        }
        return null;
    }

    private BigDecimal asBigDecimal(JsonNode node, String field) {
        if (node.has(field) && node.path(field).isNumber()) {
            return BigDecimal.valueOf(node.path(field).asDouble());
        }
        return null;
    }
}

