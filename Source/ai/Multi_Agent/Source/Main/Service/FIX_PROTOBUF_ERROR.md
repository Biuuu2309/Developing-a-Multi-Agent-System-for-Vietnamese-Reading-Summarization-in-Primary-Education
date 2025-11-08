# Sửa lỗi Protobuf Compatibility

## Lỗi:
```
TypeError: Descriptors cannot be created directly.
If this call came from a _pb2.py file, your generated code is out of date and must be regenerated with protoc >= 3.19.0.
```

## Nguyên nhân:
Xung đột giữa protobuf version mới và TensorFlow (cần protobuf 3.20.x hoặc thấp hơn)

## Giải pháp:

### Cách 1: Downgrade protobuf (Khuyến nghị)

Trong Anaconda Prompt (với pytorch-env activated):

```bash
pip install protobuf==3.20.3
```

Hoặc chạy script:
```bash
fix_protobuf.bat
```

### Cách 2: Set Environment Variable

Đã được thêm vào `run_flask_api.bat`, nhưng nếu vẫn lỗi, chạy thủ công:

```bash
# Windows
set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python flask_mas_api.py
```

### Cách 3: Kiểm tra và fix trong conda environment

```bash
# Activate environment
conda activate pytorch-env

# Kiểm tra version hiện tại
pip show protobuf

# Downgrade
pip install protobuf==3.20.3

# Hoặc nếu cần version cụ thể khác
pip install "protobuf<4.0"
```

## Sau khi fix:

1. Chạy lại `run_flask_api.bat`
2. Hoặc chạy trực tiếp:
   ```bash
   conda activate pytorch-env
   set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
   python flask_mas_api.py
   ```

## Kiểm tra đã fix:

Nếu không còn lỗi protobuf, Flask API sẽ chạy và hiển thị:
```
✅ MAS_Program imported successfully
✅ Flask app created
🚀 Starting MAS Flask API Server...
```

