# Test Flask API

## Flask API đã chạy thành công! ✅

Server đang chạy tại:
- http://localhost:8000
- http://127.0.0.1:8000
- http://192.168.10.4:8000

## Test Health Check

### Dùng trình duyệt:
Mở: http://localhost:8000/health

Kết quả mong đợi:
```json
{"status":"ok","service":"MAS Flask API"}
```

### Dùng PowerShell:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health
```

## Test Process Endpoint

### Dùng PowerShell:
```powershell
$body = @{
    conversationId = "test-123"
    userId = "user-123"
    content = "Xin chào"
    messageId = "msg-123"
    role = "USER"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/process -Method POST -Body $body -ContentType "application/json"
```

## Bây giờ bạn có thể:

1. **Giữ Flask API chạy** (giữ terminal này mở)
2. **Chạy Spring Boot** trong terminal khác
3. **Gửi request từ Spring Boot** → Flask API sẽ xử lý

## Lưu ý:

- ⚠️ **KHÔNG đóng terminal Flask API** trong khi Spring Boot đang chạy
- ✅ Flask API đã sẵn sàng nhận request từ Spring Boot
- ✅ Spring Boot sẽ gọi `http://localhost:8000/process` khi có message mới

