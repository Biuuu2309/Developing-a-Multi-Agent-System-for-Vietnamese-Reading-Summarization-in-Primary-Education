# Chạy Flask API với Conda (pytorch-env)

## Bước 1: Activate Conda environment

```powershell
conda activate pytorch-env
```

## Bước 2: Di chuyển đến thư mục Service

```powershell
cd Source/ai/Multi_Agent/Source/Main/Service
```

## Bước 3: Cài đặt dependencies

### Kiểm tra các package đã có:
```powershell
conda list | Select-String -Pattern "flask|langchain|chromadb"
```

### Cài đặt các package còn thiếu:

```powershell
# Cài đặt Flask và Flask-CORS
conda install -c conda-forge flask flask-cors -y

# Hoặc dùng pip trong conda environment
pip install flask flask-cors

# Cài đặt các package khác
pip install langchain langchain-ollama langgraph chromadb sentence-transformers python-dotenv pydantic
```

### Hoặc cài đặt tất cả từ requirements.txt:
```powershell
pip install -r requirements.txt
```

## Bước 4: Kiểm tra Ollama model

```powershell
ollama list
```

Nếu chưa có `llama3:8b`:
```powershell
ollama pull llama3:8b
```

## Bước 5: Chạy Flask API

```powershell
python flask_mas_api.py
```

## Lưu ý:

1. **Luôn activate conda environment trước khi chạy**:
   ```powershell
   conda activate pytorch-env
   ```

2. **Nếu gặp lỗi "python not found"**, thử:
   ```powershell
   # Kiểm tra Python trong environment
   conda activate pytorch-env
   python --version
   which python  # Linux/Mac
   where python  # Windows
   ```

3. **Nếu cần cài thêm package**, luôn activate environment trước:
   ```powershell
   conda activate pytorch-env
   pip install <package_name>
   ```

## Quick Start (Tất cả trong một):

```powershell
# 1. Activate environment
conda activate pytorch-env

# 2. Di chuyển đến thư mục
cd Source/ai/Multi_Agent/Source/Main/Service

# 3. Cài đặt dependencies (nếu chưa có)
pip install -r requirements.txt

# 4. Chạy Flask API
python flask_mas_api.py
```

