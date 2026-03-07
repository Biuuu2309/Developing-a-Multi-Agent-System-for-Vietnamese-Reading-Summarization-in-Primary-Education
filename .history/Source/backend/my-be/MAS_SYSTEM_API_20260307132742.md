# MAS System API Documentation

## Tổng quan

MAS System API được thiết kế để tích hợp Multi-Agent System (Python) với Spring Boot backend. Hệ thống bao gồm:

- **Database Schema**: Các bảng mới cho MAS (mas_sessions, mas_states, mas_plans, mas_evaluations, mas_goals, mas_agent_memories, mas_negotiations, mas_agent_confidences)
- **Spring Boot API**: REST API endpoints để quản lý MAS sessions, states, agents, và logs
- **Flask API**: Python API để xử lý MAS workflow và kết nối với Spring Boot

## Database Schema

Xem file `Source/database/mysql_mas.sql` để biết chi tiết về schema.

### Các bảng chính:

1. **mas_sessions**: Quản lý các session conversation với MAS
2. **mas_states**: Lưu trữ state của MAS workflow cho mỗi request
3. **mas_plans**: Lưu trữ execution plans
4. **mas_evaluations**: Lưu trữ kết quả đánh giá
5. **mas_goals**: Advanced MAS - Goal State Management
6. **mas_agent_memories**: Lưu trữ memory của từng agent
7. **mas_negotiations**: Lưu trữ negotiation history
8. **mas_agent_confidences**: Lưu trữ confidence scores của agents

## Spring Boot API Endpoints

Base URL: `http://localhost:8080/api/mas`

### 1. Chat với MAS System

**POST** `/chat`

Xử lý chat message qua MAS system.

**Request Body:**
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
  "sessionId": "session-id",
  "stateId": "state-id",
  "messageId": "message-id",
  "finalOutput": "Kết quả tóm tắt...",
  "intent": "{\"intent\": \"summarize\", ...}",
  "plan": "{\"pipeline\": [...]}",
  "summary": "Tóm tắt...",
  "evaluation": "{\"rouge1_f1\": 0.85, ...}",
  "clarificationNeeded": false,
  "clarificationQuestion": "",
  "agentConfidences": "{\"planning_agent\": 0.9, ...}",
  "status": "COMPLETED"
}
```

### 2. Tạo MAS Session

**POST** `/sessions`

Tạo session mới cho MAS conversation.

**Request Body:**
```json
{
  "userId": "user-id",
  "conversationId": "optional-conversation-id"
}
```

**Response:**
```json
{
  "sessionId": "session-id",
  "userId": "user-id",
  "conversationId": "conversation-id",
  "status": "ACTIVE",
  "createdAt": "2024-01-01T00:00:00",
  "updatedAt": "2024-01-01T00:00:00"
}
```

### 3. Lấy Sessions của User

**GET** `/sessions/user/{userId}`

Lấy tất cả sessions của một user.

**Response:**
```json
[
  {
    "sessionId": "session-id",
    "userId": "user-id",
    "conversationId": "conversation-id",
    "status": "ACTIVE",
    "createdAt": "2024-01-01T00:00:00",
    "updatedAt": "2024-01-01T00:00:00"
  }
]
```

### 4. Lấy Session theo ID

**GET** `/sessions/{sessionId}?userId={userId}`

Lấy thông tin session theo ID.

### 5. Cập nhật Session Status

**PUT** `/sessions/{sessionId}/status?status={status}`

Cập nhật status của session (ACTIVE, COMPLETED, ARCHIVED).

### 6. Lấy Session History

**GET** `/sessions/{sessionId}/history?userId={userId}`

Lấy lịch sử states của session.

### 7. Lấy Latest State

**GET** `/sessions/{sessionId}/latest-state?userId={userId}`

Lấy state mới nhất của session.

### 8. Quản lý Agents

- **POST** `/agents` - Tạo agent mới
- **GET** `/agents` - Lấy tất cả agents
- **GET** `/agents/{agentId}` - Lấy agent theo ID
- **DELETE** `/agents/{agentId}` - Xóa agent

### 9. Quản lý Agent Logs

- **GET** `/agent-logs/message/{messageId}` - Lấy logs theo message ID
- **GET** `/agent-logs/agent/{agentId}` - Lấy logs theo agent ID
- **GET** `/agent-logs/{logId}` - Lấy log theo ID

## Cấu hình

### Spring Boot (application.yaml)

```yaml
mas:
  flask:
    api:
      url: ${MAS_FLASK_API_URL:http://localhost:5000}
```

### Flask API

Chạy Flask API tại port 5000 (mặc định).

## Workflow

1. Client gửi request đến Spring Boot API (`/api/mas/chat`)
2. Spring Boot gọi Flask API (`http://localhost:5000/api/mas/chat`)
3. Flask API xử lý qua MAS System (LangGraph workflow)
4. Flask API trả kết quả về Spring Boot
5. Spring Boot lưu state và message vào database
6. Spring Boot trả response về Client

## Lưu ý

- Đảm bảo Flask API đang chạy trước khi gọi Spring Boot API
- Session ID có thể được tạo tự động nếu không cung cấp
- MAS System hỗ trợ OCR từ ảnh, tóm tắt trích xuất/diễn giải, và self-improvement loop
