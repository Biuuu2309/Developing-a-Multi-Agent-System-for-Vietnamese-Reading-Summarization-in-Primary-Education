# Hướng Dẫn Chạy Web App Đánh Giá Độ Khó Đọc Hiểu

## Cài đặt

1. Cài đặt Flask (nếu chưa có):
```bash
pip install flask
```

Hoặc cài đặt tất cả dependencies:
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

1. Chạy Flask app:
```bash
python app.py
```

2. Mở trình duyệt và truy cập:
```
http://localhost:5000
```

## Tính năng

- **Nhập văn bản**: Dán hoặc nhập văn bản tiếng Việt cần đánh giá
- **Phân tích tự động**: Hệ thống sẽ phân tích và hiển thị:
  - Độ khó dự đoán (Grade 1-5)
  - Các thang đo chi tiết với ý nghĩa
  - Quy tắc được áp dụng

## Các thang đo

Hệ thống hiển thị các thang đo sau với giải thích chi tiết:

1. **Tổng số từ**: Tổng số từ trong văn bản
2. **Số từ khác nhau**: Số lượng từ vựng độc nhất
3. **Tỷ lệ từ vựng đa dạng**: Tỷ lệ từ khác nhau/tổng số từ
4. **Tỷ lệ từ hiếm**: Tỷ lệ từ lớp 4-5 (từ khó)
5. **Tỷ lệ từ không xác định**: Tỷ lệ từ không có trong từ điển
6. **Độ khó trung bình từ vựng**: Lớp trung bình của từ vựng
7. **Số câu**: Tổng số câu
8. **Độ dài trung bình câu**: Số từ trung bình mỗi câu
9. **Độ dài câu dài nhất/ngắn nhất**
10. **Tỷ lệ câu dài**: Tỷ lệ câu >= 15 từ
11. **Độ dài trung bình từ**: Số ký tự trung bình
12. **Mật độ từ vựng**: Tỷ lệ từ vựng độc nhất

## Cấu trúc thư mục

```
CSTTUD_Project/
├── app.py                 # Flask application
├── templates/
│   └── index.html        # HTML template
├── static/
│   ├── css/
│   │   └── style.css     # CSS styling
│   └── js/
│       └── main.js       # JavaScript logic
└── requirements.txt      # Python dependencies
```
