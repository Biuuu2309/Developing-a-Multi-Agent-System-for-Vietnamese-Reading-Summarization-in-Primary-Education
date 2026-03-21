# MAS Flask API Server

Flask API server để kết nối Spring Boot với Multi-Agent System (MAS).

## Cài đặt

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Đảm bảo đã cấu hình:
   - Ollama model (mặc định: `llama3:8b`)
   - ChromaDB cho long-term memory
   - Các dependencies khác từ MAS_Program.py

## Chạy Server

```bash
python flask_mas_api.py
```

Server sẽ chạy tại: `http://localhost:8000`

## Endpoints

### POST /process
Xử lý message từ Spring Boot và trả về response từ MAS.

**Request:**
```json
{
    "conversationId": "string",
    "userId": "string",
    "content": "string",
    "messageId": "string",
    "role": "string"
}
```

**Response:**
```json
{
    "response": "string",
    "agentId": "string",
    "metadata": "string (JSON)",
    "role": "assistant"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
    "status": "ok",
    "service": "MAS Flask API"
}
```

### GET /sessions
Liệt kê tất cả các session đang active.

**Response:**
```json
{
    "conversation_sessions": {
        "conversation_id": {
            "session_id": "string",
            "user_id": "string",
            "last_activity": timestamp
        }
    },
    "active_sessions_count": number
}
```

## Cấu hình Spring Boot

Trong `application.properties` hoặc `application.yml`:

```properties
mas.api.url=http://localhost:8000/process
```

## Quản lý Session

- Mỗi `conversationId` sẽ có một session riêng trong MAS
- Session được tự động tạo khi có message đầu tiên
- Session được tiếp tục khi có message tiếp theo trong cùng conversation
- Session được lưu trong memory của MAS để duy trì context

## Lưu ý

- Đảm bảo MAS_Program.py đã được import đúng và các dependencies đã được cài đặt
- Server cần chạy trước khi Spring Boot gọi API
- CORS đã được enable để cho phép Spring Boot gọi từ frontend

