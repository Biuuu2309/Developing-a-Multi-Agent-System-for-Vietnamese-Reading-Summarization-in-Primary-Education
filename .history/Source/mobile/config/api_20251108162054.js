// API Configuration
// Thay đổi IP này thành IP máy bạn chạy Spring Boot
// Để tìm IP: ipconfig (Windows) hoặc ifconfig (Mac/Linux)

export const API_CONFIG = {
  // Development - Thay bằng IP máy bạn
  BASE_URL: __DEV__
    ? 'http://192.168.10.4:8080/api' // ⚠️ THAY ĐỔI IP NÀY
    : 'https://your-production-api.com/api',
  
  TIMEOUT: 360000, // 6 phút cho MAS xử lý
};

// Hướng dẫn tìm IP:
// 1. Windows: Mở CMD, chạy `ipconfig`, tìm "IPv4 Address"
// 2. Mac/Linux: Mở Terminal, chạy `ifconfig`, tìm "inet"
// 3. Đảm bảo Spring Boot và mobile app cùng mạng WiFi

