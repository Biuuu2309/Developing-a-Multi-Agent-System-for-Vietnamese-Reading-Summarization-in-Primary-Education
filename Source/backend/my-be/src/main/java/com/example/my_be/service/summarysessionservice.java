package com.example.my_be.service;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.cloudinary.json.JSONArray;
import org.cloudinary.json.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.orm.ObjectOptimisticLockingFailureException;
import org.springframework.web.multipart.MultipartFile;

import com.cloudinary.Cloudinary;
import com.cloudinary.utils.ObjectUtils;
import com.example.my_be.model.SummarySession;
import com.example.my_be.model.User;
import com.example.my_be.repository.SummarySessionRepository;

@Service
public class SummarySessionService {

    private final RestTemplate restTemplate;
    private final Cloudinary cloudinary;

    @Autowired
    public SummarySessionRepository summarySessionRepository;

    @Autowired
    private UserService userService;

    @Autowired
    private SummaryHistoryService summaryHistoryService;

    @Autowired
    public SummarySessionService(RestTemplateBuilder restTemplateBuilder, Cloudinary cloudinary) {
        this.restTemplate = restTemplateBuilder.build();
        this.cloudinary = cloudinary;
    }

    @Transactional
    public SummarySession createSummarySession(SummarySession session) {
        String contentHash = computeHash(session.getContent());
        session.setContentHash(contentHash);
        return summarySessionRepository.save(session);
    }

    public Optional<SummarySession> getSummarySessionById(Long sessionId) {
        return summarySessionRepository.findById(sessionId);
    }

    public SummarySession updateSummarySession(SummarySession session) {
        return summarySessionRepository.save(session);
    }

    public void deleteSummarySession(Long sessionId) {
        try {
            summarySessionRepository.deleteById(sessionId);
        } catch (EmptyResultDataAccessException | ObjectOptimisticLockingFailureException ex) {
            // Treat as already deleted (idempotent delete)
        }
    }

    public Optional<SummarySession> getSummarySessionByUserAndContent(User createdBy, String content) {
        return summarySessionRepository.findByCreatedByAndContent(createdBy, content);
    }

    public List<SummarySession> findSessionsByUser(User user) {
        return summarySessionRepository.findByCreatedBy(user);
    }

    public class ImageUploadResult {
        private final String imageUrl;
        private final boolean success;

        public ImageUploadResult(String imageUrl, boolean success) {
            this.imageUrl = imageUrl;
            this.success = success;
        }

        public String getImageUrl() {
            return imageUrl;
        }

        public boolean isSuccess() {
            return success;
        }
    }

    @Value("${gemini.api-key}")
    private String geminiApiKey;

    public ImageUploadResult generateImageAndUploadToCloudinary(String content) {
        String url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=" + geminiApiKey;

        JSONObject request = new JSONObject();
        JSONObject contents = new JSONObject();
        JSONArray parts = new JSONArray();
        JSONObject part = new JSONObject();
        part.put("text", "Bạn là một họa sĩ minh họa chuyên nghiệp. Hãy tạo một hình ảnh minh họa theo phong cách Hoạt hình Chibi 2D. Yêu cầu: ASPECT RATIO: 16:9,CHỈ TẠO HÌNH ẢNH, KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO VÀO ẢNH. Nội dung tham khảo: " + content);
        parts.put(part);
        contents.put("parts", parts);
        request.put("contents", contents);

        JSONObject generationConfig = new JSONObject();
        generationConfig.put("responseModalities", new String[] { "Text", "Image" });
        request.put("generationConfig", generationConfig);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<String> entity = new HttpEntity<>(request.toString(), headers);

        ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
        if (response.getStatusCode().is2xxSuccessful()) {
            System.out.println("API Gemini trả về thành công!");
            System.out.println("Raw response: " + response.getBody());
            JSONObject jsonObject = new JSONObject(response.getBody());
            JSONArray candidates = jsonObject.getJSONArray("candidates");
            JSONObject candidate = candidates.getJSONObject(0);
            JSONObject contentObject = candidate.getJSONObject("content");
            JSONArray partsArray = contentObject.getJSONArray("parts");
            JSONObject partObject = partsArray.getJSONObject(1);
            
            // Check if inlineData exists
            if (partObject.has("inlineData")) {
                JSONObject inlineData = partObject.getJSONObject("inlineData");
                String base64Content = inlineData.getString("data");

                // System.out.println("Base64 hình ảnh đã được tạo: " + base64Content.substring(0, 100) + "...");

                byte[] decodedBytes = Base64.getDecoder().decode(base64Content);
                File tempFile = null;
                try {
                    tempFile = File.createTempFile("image", ".png");
                    try (FileOutputStream fos = new FileOutputStream(tempFile)) {
                        fos.write(decodedBytes);
                    }

                    @SuppressWarnings("unchecked")
                    Map<String, Object> params = ObjectUtils.asMap(
                            "folder", "summary_sessions",
                            "use_filename", true,
                            "unique_filename", false,
                            "overwrite", true);

                    @SuppressWarnings("unchecked")
                    Map<String, Object> uploadResult = cloudinary.uploader().upload(tempFile, params);
                    String imageUrl = (String) uploadResult.get("secure_url");
                    System.out.println("URL hình ảnh trên Cloudinary: " + imageUrl);
                    System.out.println("Hình ảnh đã được tải lên Cloudinary thành công!");
                    return new ImageUploadResult(imageUrl, true);
                } catch (IOException e) {
                    throw new RuntimeException("Failed to create or upload temporary file", e);
                } finally {
                    if (tempFile != null) {
                        tempFile.delete();
                    }
                }
            } else {
                System.out.println("No inlineData found in response. Response structure:");
                System.out.println("Part object: " + partObject.toString());
                return new ImageUploadResult(null, false);
            }
        } else {
            System.out.println("API Gemini trả về thất bại!");
            return new ImageUploadResult(null, false);
        }
    }

    // New method to upload an image to Cloudinary
    public ImageUploadResult uploadImageToCloudinary(MultipartFile file) {
        File tempFile = null;
        try {
            // Convert MultipartFile to File
            tempFile = File.createTempFile("upload", file.getOriginalFilename());
            try (FileOutputStream fos = new FileOutputStream(tempFile)) {
                fos.write(file.getBytes());
            }

            // Upload to Cloudinary
            @SuppressWarnings("unchecked")
            Map<String, Object> params = ObjectUtils.asMap(
                    "folder", "summary_sessions",
                    "use_filename", true,
                    "unique_filename", false,
                    "overwrite", true);

            @SuppressWarnings("unchecked")
            Map<String, Object> uploadResult = cloudinary.uploader().upload(tempFile, params);
            String imageUrl = (String) uploadResult.get("secure_url");
            System.out.println("URL hình ảnh trên Cloudinary: " + imageUrl);
            System.out.println("Hình ảnh đã được tải lên Cloudinary thành công!");
            return new ImageUploadResult(imageUrl, true);
        } catch (IOException e) {
            throw new RuntimeException("Failed to upload image to Cloudinary: " + e.getMessage(), e);
        } finally {
            if (tempFile != null) {
                tempFile.delete();
            }
        }
    }

    private String computeHash(String content) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hashBytes = digest.digest(content.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(hashBytes);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("Hashing algorithm not found", e);
        }
    }

    public SummarySession startSession(String userId, String content, String method) {
        User createdBy = userService.getUserById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));

        String contentHash = computeHash(content);
        Optional<SummarySession> existingSession = summarySessionRepository
                .findByCreatedByAndContentHash(createdBy, contentHash);

        if (existingSession.isPresent()) {
            SummarySession session = existingSession.get();
            summaryHistoryService.createSummaryHistory(session, method, content);
            return session;
        } else {
            SummarySession newSession = new SummarySession();
            newSession.setCreatedBy(createdBy);
            newSession.setContent(content);
            newSession.setContentHash(contentHash);
            summarySessionRepository.save(newSession);
            summaryHistoryService.createSummaryHistory(newSession, method, content);
            return newSession;
        }
    }
}
