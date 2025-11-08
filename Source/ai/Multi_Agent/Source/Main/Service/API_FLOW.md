# Luồng xử lý API - Spring Boot ↔ Flask ↔ MAS

## Tổng quan luồng:

```
Frontend → Spring Boot → Flask API → MAS → Flask API → Spring Boot → Frontend
```

---

## Chi tiết từng bước:

### 1. Frontend gửi request → Spring Boot

**Endpoint:** `POST /api/message/create`

**Request Body:**
```json
{
    "conversationId": "74082d5c-28bf-404e-a599-fa786c2cc742",
    "userId": "557fd328-83f0-4231-80df-ff6f4a289d03",
    "content": "Xin chào",
    "agentId": null,
    "role": "USER",
    "metadata": null
}
```

**Controller:** `MessageController.createMessage()`
- Nhận request từ frontend
- Gọi `MessageNewService.createMessage()`

---

### 2. Spring Boot xử lý request

**Service:** `MessageNewService.createMessage()`

**Bước 2.1: Lưu user message vào database**
```java
Message userMessage = new Message();
userMessage.setMessageId(UUID.randomUUID().toString());
userMessage.setConversationId(request.getConversationId());
userMessage.setUserId(request.getUserId());
userMessage.setRole(MessageRole.USER);
userMessage.setContent(request.getContent());
userMessage.setStatus(MessageStatus.PENDING);
messageRepository.save(userMessage);
```

**Bước 2.2: Chuẩn bị request cho Flask API**
```java
MASRequest masRequest = new MASRequest();
masRequest.setConversationId(request.getConversationId());
masRequest.setUserId(request.getUserId());
masRequest.setContent(request.getContent());
masRequest.setMessageId(messageId);
masRequest.setRole(request.getRole());
```

**Bước 2.3: Kiểm tra Flask API health**
```java
String healthUrl = masApiUrl.replace("/process", "/health");
restTemplate.getForEntity(healthUrl, String.class);
```

**Bước 2.4: Gọi Flask API**
```java
// URL: http://localhost:8000/process
// Method: POST
// Headers: Content-Type: application/json
// Body: MASRequest (JSON)
ResponseEntity<String> response = restTemplate.postForEntity(masApiUrl, entity, String.class);
```

**Bước 2.5: Cập nhật status**
- Trước khi gọi: `PENDING` → `PROCESSING`
- Sau khi nhận response: `PROCESSING` → `COMPLETED` hoặc `FAILED`

---

### 3. Flask API nhận request

**Endpoint:** `POST /process`

**File:** `flask_mas_api.py`

**Bước 3.1: Parse request**
```python
data = request.get_json()
conversation_id = data.get("conversationId")
user_id = data.get("userId")
content = data.get("content")
```

**Bước 3.2: Quản lý session**
```python
# Kiểm tra xem conversation_id đã có session chưa
session_info = conversation_session_map.get(conversation_id)
session_id = session_info.get("session_id") if session_info else None
```

**Bước 3.3: Gọi MAS handler**
```python
result = process_message_api(
    app=app,
    create_initial_state=create_initial_state,
    user_input=content,
    conversation_id=conversation_id,
    user_id=user_id,
    session_id=session_id
)
```

---

### 4. MAS xử lý message

**File:** `mas_api_handler.py`

**Bước 4.1: Quản lý session**
```python
if session_id:
    # Tiếp tục session cũ
    memory_manager.resume_session(session_id, user_id, replay_last_n=20)
    initial_state = build_state_from_memory(user_id, max_messages=20)
else:
    # Tạo session mới hoặc lấy session hiện tại
    stm = memory_manager.get_memory(user_id)
    if not stm.session_id or not stm.conversation_history:
        new_session_id = memory_manager.start_new_session(user_id)
        initial_state = create_initial_state()
    else:
        initial_state = build_state_from_memory(user_id, max_messages=20)
```

**Bước 4.2: Thêm user message**
```python
memory_manager.add_message("user", user_input, user_id=user_id)
initial_state["messages"].append(HumanMessage(content=user_input))
initial_state["needs_user_input"] = False
initial_state["input_classification"] = None
```

**Bước 4.3: Chạy MAS workflow**
```python
# LangGraph workflow xử lý qua các agents:
# coordinator_agent → input_classifier_agent → ocr_agent → 
# spellchecker_agent → extractor_agent/abstracter_agent → 
# grade_calibrator_agent → evaluator_agent → aggregator_agent
state = app.invoke(initial_state, config={"recursion_limit": 50})
```

**Bước 4.4: Trích xuất response**
```python
last_message = state["messages"][-1]  # Message cuối cùng từ assistant
response_text = last_message.content
agent_id = state.get("current_agent", "coordinator_agent")

# Tạo metadata
metadata = {
    "conversation_stage": state.get("conversation_stage"),
    "summary_type": state.get("summary_type"),
    "grade_level": state.get("grade_level", 0),
    "needs_user_input": state.get("needs_user_input", False)
}

# Lấy session_id
current_session_id = memory_manager.get_session_id(user_id)
```

**Bước 4.5: Trả về kết quả**
```python
return {
    "response": response_text,
    "agent_id": agent_id,
    "metadata": json.dumps(metadata),
    "session_id": current_session_id,
    "needs_user_input": state.get("needs_user_input", False)
}
```

---

### 5. Flask API trả về response

**File:** `flask_mas_api.py`

**Bước 5.1: Lưu session mapping**
```python
if result.get("session_id"):
    conversation_session_map[conversation_id] = {
        "session_id": result["session_id"],
        "user_id": user_id,
        "last_activity": time.time()
    }
```

**Bước 5.2: Tạo response theo format MASResponse**
```python
response = {
    "response": result.get("response", ""),
    "agentId": result.get("agent_id", "coordinator_agent"),
    "metadata": result.get("metadata", "{}"),
    "role": "assistant"
}
return jsonify(response), 200
```

---

### 6. Spring Boot nhận response

**Service:** `MessageNewService.createMessage()`

**Bước 6.1: Parse response**
```java
MASResponse masResponse = objectMapper.readValue(response.getBody(), MASResponse.class);
```

**Bước 6.2: Lưu assistant message vào database**
```java
Message assistantMessage = new Message();
assistantMessage.setMessageId(UUID.randomUUID().toString());
assistantMessage.setConversationId(request.getConversationId());
assistantMessage.setUserId(request.getUserId());
assistantMessage.setAgentId(masResponse.getAgentId());
assistantMessage.setRole(MessageRole.ASSISTANT);
assistantMessage.setContent(masResponse.getResponse());
assistantMessage.setMetadata(masResponse.getMetadata());
assistantMessage.setStatus(MessageStatus.COMPLETED);
messageRepository.save(assistantMessage);
```

**Bước 6.3: Cập nhật user message status**
```java
savedMessage.setStatus(MessageStatus.COMPLETED);
messageRepository.save(savedMessage);
```

**Bước 6.4: Trả về response cho frontend**
```java
return mapToResponse(savedMessage);
```

---

### 7. Frontend nhận response

**Response:**
```json
{
    "messageId": "...",
    "conversationId": "...",
    "userId": "...",
    "agentId": null,
    "role": "USER",
    "content": "Xin chào",
    "metadata": null,
    "status": "COMPLETED",
    "createdAt": "2025-11-08T14:08:19"
}
```

**Lưu ý:** Frontend cần gọi API khác để lấy assistant message:
- `GET /api/message/conversation/{conversationId}` - Lấy tất cả messages trong conversation

---

## Luồng xử lý lỗi:

### Nếu Flask API không chạy:
1. Spring Boot gọi health check → **Connection refused**
2. Throw `ResourceAccessException`
3. User message status → `FAILED`
4. Trả về error cho frontend

### Nếu MAS xử lý lỗi:
1. MAS throw exception
2. Flask API catch và trả về error response (500)
3. Spring Boot nhận error response
4. User message status → `FAILED`
5. Trả về error cho frontend

---

## Timeout:

- **Connection timeout:** 5 giây (nếu không kết nối được Flask API)
- **Read timeout:** 120 giây (cho MAS xử lý)

---

## Session Management:

- Mỗi `conversationId` có một `session_id` riêng trong MAS
- Session được lưu trong `conversation_session_map` (Flask API)
- Session được tiếp tục khi có message tiếp theo trong cùng conversation
- Session được lưu trong long-term memory của MAS

---

## Database:

**2 messages được lưu:**
1. **User message:** Status từ `PENDING` → `PROCESSING` → `COMPLETED`
2. **Assistant message:** Status = `COMPLETED` ngay từ đầu

