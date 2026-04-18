# Hệ thống tóm tắt bài đọc Tiểu học (Multi-Agent System)

- Dự án xây dựng ứng dụng hỗ trợ **tóm tắt văn bản tiếng Việt** theo **trình độ lớp**, kết hợp **hệ đa tác tử (MAS)** điều phối các bước: nhận diện ý định, làm rõ yêu cầu, lập kế hoạch, OCR (khi có ảnh), tóm tắt trích xuất/diễn giải và đánh giá chất lượng — có thể lặp cải thiện kết quả.
- Dự án không công khai toàn bộ, nếu bạn có nhu cầu tham khảo, cảm phiền hãy vào mục `\Report` hoặc `\Source\ai\Multi_Agent_System\Main\MAS.ipynb`.
## Tác giả

- **Sinh viên:** Nguyễn Minh Vũ — MSSV: `2211110063`
## Kiến trúc tổng quan

```
[React + Vite]  →  [Spring Boot API :8081]  →  [Flask MAS API :5000]  →  [Python MAS / LangGraph]
                         ↓
                   [MySQL]
```

- **Frontend:** giao diện người dùng, tương tác phiên tóm tắt / MAS.
- **Backend (Spring Boot):** REST API, người dùng, phiên, tin nhắn, bản tóm tắt; proxy tới Flask khi gọi MAS (`mas.flask.api.url`, mặc định `http://localhost:5000`).
- **Flask MAS API:** cầu nối HTTP tới pipeline Python (MAS).
- **Hệ MAS (Python):** LangGraph — các node `intent` → `clarification` → `planning` → (`ocr` nếu cần) → `summarize` → `evaluate`, vòng cải thiện khi cần.

## Công nghệ chính

| Thành phần | Công nghệ |
|------------|-----------|
| Frontend | React 19, Vite 7, Tailwind CSS, React Router |
| Backend | Spring Boot 3.4, Java 21, Spring Data JPA, MySQL |
| MAS bridge | Flask (`Source/backend/flask-mas-api`) |
| MAS lõi | Python, LangGraph, các agent (Intent, Clarification, Planning, Image2Text, Abstracter, Extractor, Evaluation, …) |
| Xử lý ngôn ngữ | VnCoreNLP, mô hình tóm tắt (ViT5 / PhoBERT), OCR (ví dụ Qwen2.5-VL qua Ollama — theo cấu hình trong mã) |
| CSDL | MySQL (schema tham khảo: `Source/database/mysql.sql`) |

## Cấu trúc thư mục (rút gọn)

```
Project_NguyenMinhVu_2211110063/
├── README.md
├── Report/                    # Báo cáo / tài liệu khóa luận (nếu có)
├── Source/
│   ├── frontend/            # Ứng dụng web React + Vite
│   ├── backend/
│   │   ├── my-be/           # Spring Boot API
│   │   └── flask-mas-api/    # Flask — kết nối MAS Python
│   ├── ai/
│   │   ├── Multi_Agent_System/   # Agent, LangGraph (ví dụ Main/System_2/MAS_main.py)
│   │   ├── Model Train/          # Huấn luyện / checkpoint mô hình
│   │   └── VnCoreNLP-master/     # Bộ tách từ / POS / NER (đường dẫn cấu hình trong code)
│   └── database/              # Script SQL
```

## Yêu cầu môi trường

- **JDK 21**, **Maven**
- **Node.js** (khuyến nghị LTS) — cho frontend
- **Python 3.x** — cho Flask MAS và pipeline MAS (xem `requirements.txt` trong `flask-mas-api` và dependencies của `Multi_Agent_System`)
- **MySQL** — tạo DB và cấu hình trong `application.properties` của `my-be`
- **Ollama / mô hình cục bộ** (nếu dùng OCR/Image2Text như trong `MAS_main.py`) — cần cài đặt và bật dịch vụ theo hướng dẫn môi trường của bạn

## Chạy nhanh (phát triển)

### 1. Cơ sở dữ liệu

- Import hoặc chạy script trong `Source/database/mysql.sql` (chỉnh tên database/user/password cho khớp).

### 2. Spring Boot (`my-be`)

```bash
cd Source/backend/my-be
# Cấu hình spring.datasource.* trong src/main/resources/application.properties
mvn spring-boot:run
```

Mặc định cổng: **8081** (`server.port=8081`).

### 3. Flask MAS API

```bash
cd Source/backend/flask-mas-api
pip install -r requirements.txt
python app.py
```

Mặc định: **http://localhost:5000** — trùng với `mas.flask.api.url` của Spring.

### 4. Frontend

```bash
cd Source/frontend
npm install
npm run dev
```

Theo mặc định Vite thường chạy tại **http://localhost:5173** (xem terminal sau khi `npm run dev`).

### 5. Pipeline MAS Python

- Đường dẫn tới **VnCoreNLP JAR**, **checkpoint mô hình tóm tắt**, và (nếu có) **OCR** được khai báo trong mã (ví dụ `MAS_main.py`). Cần chỉnh cho đúng máy bạn trước khi chạy end-to-end.

## API MAS (Spring) — tham khảo

Base path: `/api/mas`

- `POST /chat` — xử lý tin nhắn qua MAS (Spring gọi Flask rồi lưu trạng thái/phiên theo logic dịch vụ).
- `POST /sessions`, `GET /sessions/user/{userId}`, `GET /sessions/{sessionId}`, … — quản lý phiên.
- `GET /sessions/{sessionId}/history`, `GET .../latest-state` — lịch sử / trạng thái.
- `GET/POST/DELETE /agents` — metadata agent (góc quản trị).
- `GET /agent-logs/...` — nhật ký agent.

Chi tiết request/response Flask: xem `Source/backend/flask-mas-api/README.md`.

## Giấy phép / ghi chú

- Mã nguồn phục vụ mục đích học thuật / khóa luận. Thành phần bên thứ ba (thư viện, mô hình) tuân theo giấy phép tương ứng của từng gói.
---

