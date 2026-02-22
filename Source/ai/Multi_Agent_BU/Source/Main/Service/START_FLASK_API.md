# Hướng dẫn chạy Flask MAS API

## Bước 1: Cài đặt dependencies

Mở terminal và chạy:

```bash
cd Source/ai/Multi_Agent/Source/Main/Service
pip install -r requirements.txt
```

Hoặc cài đặt từng package:

```bash
pip install flask flask-cors langchain langchain-ollama langgraph chromadb sentence-transformers python-dotenv pydantic
```

## Bước 2: Kiểm tra Ollama model

Đảm bảo Ollama đã cài đặt và model `llama3:8b` đã được tải:

```bash
# Kiểm tra Ollama có chạy không
ollama list

# Nếu chưa có llama3:8b, tải về
ollama pull llama3:8b
```

## Bước 3: Chạy Flask API

### Cách 1: Chạy trực tiếp

```bash
cd Source/ai/Multi_Agent/Source/Main/Service
python flask_mas_api.py
```

### Cách 2: Chạy với Python module

```bash
cd Source/ai/Multi_Agent/Source/Main/Service
python -m flask_mas_api
```

### Cách 3: Chạy với Python -u (unbuffered output)

```bash
cd Source/ai/Multi_Agent/Source/Main/Service
python -u flask_mas_api.py
```

## Bước 4: Kiểm tra Flask API đã chạy

Bạn sẽ thấy output như sau:

```
🔄 Initializing Flask MAS API...
✅ Added project root to path: ...
📦 Importing MAS_Program...
✅ MAS_Program imported successfully
📦 Importing mas_api_handler...
✅ mas_api_handler imported successfully
📦 Importing memory_manager...
✅ memory_manager imported successfully
✅ Flask app created
🚀 Starting MAS Flask API Server...
📡 Endpoint: http://localhost:8000/process
💚 Health check: http://localhost:8000/health
 * Serving Flask app 'flask_mas_api'
 * Debug mode: on
 * Running on http://127.0.0.1:8000
 * Running on http://0.0.0.0:8000
```

## Bước 5: Test Flask API

Mở terminal khác và test:

### Test health check:
```bash
# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health -Method GET

# Windows CMD hoặc Linux/Mac
curl http://localhost:8000/health
```

Kết quả mong đợi:
```json
{"status":"ok","service":"MAS Flask API"}
```

### Test process endpoint:
```bash
# Windows PowerShell
$body = @{
    conversationId = "test-123"
    userId = "user-123"
    content = "Xin chào"
    messageId = "msg-123"
    role = "USER"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/process -Method POST -Body $body -ContentType "application/json"
```

## Lưu ý quan trọng:

1. **Flask API phải chạy TRƯỚC Spring Boot**
2. **Port 8000 phải còn trống** (nếu bị chiếm, sửa port trong `flask_mas_api.py`)
3. **Đảm bảo Ollama đang chạy** và model đã được tải
4. **Giữ terminal Flask API mở** trong khi Spring Boot đang chạy

## Troubleshooting:

### Lỗi: "Address already in use"
- Port 8000 đang bị sử dụng
- Giải pháp: Tìm và kill process đang dùng port 8000, hoặc đổi port

### Lỗi: "Module not found"
- Thiếu dependencies
- Giải pháp: Chạy `pip install -r requirements.txt`

### Lỗi: "Ollama connection error"
- Ollama chưa chạy hoặc model chưa tải
- Giải pháp: Chạy `ollama serve` và `ollama pull llama3:8b`

### Flask API bị đứng khi import MAS_Program
- Có thể do code trong MAS_Program.py chạy khi import
- Giải pháp: Đã sửa trong code, restart Flask API

