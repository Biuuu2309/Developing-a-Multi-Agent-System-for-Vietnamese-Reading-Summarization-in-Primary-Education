# Hướng dẫn Setup Chat Screen

## Đã tạo:

1. **Chat UI** (`app/(tabs)/summary-demo.js`):
   - Giao diện giống ChatGPT
   - FlatList hiển thị messages
   - TextInput để nhập
   - Loading indicators
   - Auto-scroll khi có message mới

2. **API Service** (`services/api.js`):
   - Tích hợp với Spring Boot API
   - Functions: `createMessage`, `getMessagesByConversation`, `createConversation`

3. **Config** (`config/api.js`):
   - Cấu hình API URL
   - Timeout settings

## Cấu hình:

### Bước 1: Cập nhật API URL

Mở file `Source/mobile/config/api.js` và thay đổi IP:

```javascript
BASE_URL: __DEV__
  ? 'http://YOUR_IP:8080/api' // ⚠️ Thay YOUR_IP bằng IP máy bạn
  : 'https://your-production-api.com/api',
```

**Cách tìm IP:**
- **Windows**: Mở CMD, chạy `ipconfig`, tìm "IPv4 Address"
- **Mac/Linux**: Mở Terminal, chạy `ifconfig`, tìm "inet"
- **Lưu ý**: Đảm bảo Spring Boot và mobile app cùng mạng WiFi

### Bước 2: Cập nhật User ID

Mở file `Source/mobile/app/(tabs)/summary-demo.js` và thay đổi:

```javascript
const [userId] = useState('YOUR_USER_ID'); // Thay bằng user ID thực tế
```

### Bước 3: Chạy ứng dụng

```bash
cd Source/mobile
npm install  # Nếu chưa cài dependencies
npm start
```

## Tính năng:

✅ **Giao diện giống ChatGPT:**
- User messages: Màu xanh, bên phải
- Assistant messages: Màu xám, bên trái
- Rounded corners
- Auto-scroll khi có message mới

✅ **Loading states:**
- "Đang gửi..." khi gửi message
- "Đang xử lý..." khi MAS đang xử lý
- Disable input khi đang xử lý

✅ **Error handling:**
- Alert khi có lỗi
- Retry mechanism

✅ **Session management:**
- Tự động tạo conversation mới
- Load messages khi vào màn hình
- Refresh messages sau khi gửi

## Luồng hoạt động:

1. **Khởi tạo:**
   - Tạo conversation mới
   - Load messages cũ (nếu có)

2. **Gửi message:**
   - User nhập text → Click "Gửi"
   - Hiển thị message ngay (pending)
   - Gọi API `POST /api/message/create`
   - Spring Boot → Flask API → MAS
   - Nhận response → Refresh messages

3. **Hiển thị messages:**
   - Load từ API `GET /api/message/conversation/{id}`
   - Hiển thị theo thứ tự thời gian
   - Auto-scroll đến message mới nhất

## Troubleshooting:

### Lỗi: "Network request failed"
- Kiểm tra Spring Boot đang chạy
- Kiểm tra IP trong `config/api.js` đúng chưa
- Kiểm tra cùng mạng WiFi

### Lỗi: "Timeout"
- MAS xử lý lâu (>120s)
- Có thể tăng timeout trong `config/api.js`

### Messages không hiển thị
- Kiểm tra API response format
- Kiểm tra console logs
- Kiểm tra conversationId có đúng không

## Cải thiện có thể thêm:

- [ ] Pull to refresh
- [ ] Image support
- [ ] Voice input
- [ ] Message timestamps
- [ ] Typing indicator
- [ ] Message status (sent, delivered, read)
- [ ] Dark mode support (đã có sẵn)

