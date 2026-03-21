# Troubleshooting - Flask MAS API

## Vấn đề: Chương trình bị đứng khi gọi MAS API

### Nguyên nhân có thể:

1. **Flask API chưa chạy**
   - Spring Boot đang cố gọi Flask API nhưng Flask chưa được khởi động
   - **Giải pháp**: Chạy Flask API trước khi chạy Spring Boot

2. **Flask API gặp lỗi khi import MAS_Program**
   - MAS_Program.py có thể gặp lỗi khi import
   - **Giải pháp**: Kiểm tra log của Flask API khi khởi động

3. **Timeout quá dài**
   - MAS xử lý mất nhiều thời gian
   - **Giải pháp**: Đã cấu hình timeout 120 giây cho read timeout

## Cách kiểm tra:

### 1. Kiểm tra Flask API có chạy không:

```bash
# Chạy Flask API
cd Source/ai/Multi_Agent/Source/Main/Service
python flask_mas_api.py
```

Bạn sẽ thấy:
```
🔄 Initializing Flask MAS API...
✅ Added project root to path: ...
📦 Importing MAS_Program...
✅ MAS_Program imported successfully
...
🚀 Starting MAS Flask API Server...
📡 Endpoint: http://localhost:8000/process
💚 Health check: http://localhost:8000/health
```

### 2. Test Flask API bằng curl:

```bash
# Health check
curl http://localhost:8000/health

# Test process endpoint
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "test-123",
    "userId": "user-123",
    "content": "Xin chào",
    "messageId": "msg-123",
    "role": "USER"
  }'
```

### 3. Kiểm tra Spring Boot logs:

Khi gọi API, bạn sẽ thấy:
```
MAS API URL: http://localhost:8000/process
MAS API entity: ...
Calling MAS API...
MAS API response status: 200 OK
MAS API response body: ...
```

Nếu thấy lỗi:
- `ResourceAccessException`: Flask API chưa chạy hoặc không thể kết nối
- `HttpClientErrorException`: Request không hợp lệ (400, 404, etc.)
- `HttpServerErrorException`: Flask API gặp lỗi (500, etc.)

### 4. Kiểm tra Flask API logs:

Khi nhận request, Flask API sẽ log:
```
📨 Received request at /process
📝 Request data: conversationId=..., userId=..., content=...
🔄 Processing message through MAS...
✅ MAS processing completed
✅ Sending response: agentId=..., response length=...
```

Nếu có lỗi, sẽ thấy:
```
❌ Error importing MAS_Program: ...
```

## Các bước khắc phục:

1. **Đảm bảo Flask API đang chạy**:
   ```bash
   cd Source/ai/Multi_Agent/Source/Main/Service
   python flask_mas_api.py
   ```

2. **Kiểm tra port 8000 có bị chiếm không**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

3. **Kiểm tra dependencies đã cài đặt**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Kiểm tra Ollama model đã tải**:
   ```bash
   ollama list
   # Nếu chưa có llama3:8b
   ollama pull llama3:8b
   ```

5. **Kiểm tra MAS_Program.py có lỗi không**:
   ```bash
   cd Source/ai/Multi_Agent/Source/Main/Program_Main
   python -c "from MAS_Program import app, create_initial_state; print('OK')"
   ```

## Timeout Configuration:

- **Connection timeout**: 5 giây (nếu không kết nối được trong 5 giây sẽ báo lỗi)
- **Read timeout**: 120 giây (MAS có thể cần thời gian xử lý)

Nếu MAS xử lý lâu hơn 120 giây, có thể tăng timeout trong `AppConfig.java`:
```java
factory.setReadTimeout(300000); // 5 phút
```

