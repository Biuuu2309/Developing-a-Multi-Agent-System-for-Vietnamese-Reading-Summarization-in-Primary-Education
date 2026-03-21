# Quick Start - Chạy Flask API

## Cách 1: Dùng Script Batch (Dễ nhất) ⭐

1. **Double-click file**: `run_flask_api.bat`
2. Script sẽ tự động:
   - Tìm và activate conda
   - Activate environment `pytorch-env`
   - Cài đặt dependencies
   - Chạy Flask API

## Cách 2: Dùng Anaconda Prompt

1. **Mở Anaconda Prompt** (từ Start Menu)
2. Chạy các lệnh sau:

```bash
conda activate pytorch-env
cd E:\Project_NguyenMinhVu_2211110063\Source\ai\Multi_Agent\Source\Main\Service
pip install -r requirements.txt
python flask_mas_api.py
```

## Cách 3: Activate thủ công trong PowerShell

Nếu bạn biết đường dẫn conda (ví dụ: `C:\Users\minhv\anaconda3`):

```powershell
# Activate conda
& "C:\Users\minhv\anaconda3\Scripts\activate.bat" pytorch-env

# Di chuyển đến thư mục
cd E:\Project_NguyenMinhVu_2211110063\Source\ai\Multi_Agent\Source\Main\Service

# Chạy Flask API
python flask_mas_api.py
```

## Kiểm tra đã activate thành công

Sau khi activate, bạn sẽ thấy `(pytorch-env)` ở đầu dòng:

```
(pytorch-env) PS E:\Project_NguyenMinhVu_2211110063\Source\ai\Multi_Agent\Source\Main\Service>
```

## Nếu gặp lỗi

### Lỗi: "conda is not recognized"
→ Dùng Anaconda Prompt thay vì PowerShell thông thường

### Lỗi: "environment pytorch-env not found"
→ Kiểm tra tên environment: `conda env list`
→ Hoặc tạo mới: `conda create -n pytorch-env python=3.9`

### Lỗi: "pip is not recognized"
→ Đảm bảo đã activate environment: `conda activate pytorch-env`
→ Thử: `python -m pip install -r requirements.txt`

### Lỗi: "Module not found"
→ Cài đặt lại: `pip install -r requirements.txt`

## Kết quả mong đợi

Khi Flask API chạy thành công, bạn sẽ thấy:

```
🔄 Initializing Flask MAS API...
✅ MAS_Program imported successfully
✅ Flask app created
🚀 Starting MAS Flask API Server...
📡 Endpoint: http://localhost:8000/process
💚 Health check: http://localhost:8000/health
 * Running on http://127.0.0.1:8000
```

**Giữ terminal này mở** trong khi Spring Boot đang chạy!

