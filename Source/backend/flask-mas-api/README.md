# MAS Flask API

Flask API để kết nối Multi-Agent System (Python) với Spring Boot backend.

## Cài đặt

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Đảm bảo MAS System đã được cấu hình đúng trong `Source/ai/Multi_Agent_System/Main/System 2/MAS_main.ipynb`

## Chạy

```bash
python app.py
```

API sẽ chạy tại `http://localhost:5000`

## API Endpoints

### POST /api/mas/chat
Xử lý chat message qua MAS system.

**Request:**
```json
{
  "sessionId": "optional-session-id",
  "userId": "user-id",
  "userInput": "Hãy tóm tắt văn bản sau: ...",
  "conversationId": "optional-conversation-id"
}
```

**Response:**
```json
{
  "session_id": "session-id",
  "final_output": "Kết quả tóm tắt...",
  "intent": "{\"intent\": \"summarize\", ...}",
  "plan": "{\"pipeline\": [...]}",
  "summary": "Tóm tắt...",
  "evaluation": "{\"rouge1_f1\": 0.85, ...}",
  "clarification_needed": false,
  "clarification_question": "",
  "agent_confidences": "{\"planning_agent\": 0.9, ...}",
  "status": "COMPLETED"
}
```

### GET /api/mas/session/{session_id}/history
Lấy lịch sử conversation của session.

**Response:**
```json
{
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### GET /api/mas/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "MAS Flask API"
}
```
