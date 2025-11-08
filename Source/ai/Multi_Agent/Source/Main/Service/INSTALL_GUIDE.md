# Hướng dẫn cài đặt và chạy Flask API trên Windows

## Vấn đề: "pip is not recognized"

Nếu gặp lỗi này, có thể do:
1. Python chưa được cài đặt
2. Python chưa được thêm vào PATH
3. Cần dùng `py` thay vì `python` trên Windows

## Giải pháp:

### Cách 1: Dùng Python Launcher (py)

Trên Windows, thử dùng `py` thay vì `python`:

```powershell
# Kiểm tra Python
py --version

# Cài đặt dependencies
py -m pip install -r requirements.txt

# Chạy Flask API
py flask_mas_api.py
```

### Cách 2: Tìm đường dẫn Python

Nếu bạn đã cài Python nhưng không có trong PATH:

```powershell
# Tìm Python trong các vị trí thường gặp
Get-ChildItem -Path "C:\Users\$env:USERNAME\AppData\Local\Programs\Python" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue
Get-ChildItem -Path "C:\Python*" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue
```

Sau đó dùng đường dẫn đầy đủ:
```powershell
C:\Users\minhv\AppData\Local\Programs\Python\Python3XX\python.exe -m pip install -r requirements.txt
```

### Cách 3: Cài đặt Python mới

1. Tải Python từ: https://www.python.org/downloads/
2. **QUAN TRỌNG**: Khi cài đặt, chọn "Add Python to PATH"
3. Restart terminal sau khi cài đặt
4. Chạy lại: `python -m pip install -r requirements.txt`

### Cách 4: Dùng Anaconda/Miniconda

Nếu bạn dùng Anaconda:
```powershell
conda install flask flask-cors
conda install -c conda-forge langchain langchain-ollama
pip install langgraph chromadb sentence-transformers python-dotenv pydantic
```

## Cài đặt dependencies:

### Nếu dùng `py`:
```powershell
cd Source/ai/Multi_Agent/Source/Main/Service
py -m pip install flask flask-cors langchain langchain-ollama langgraph chromadb sentence-transformers python-dotenv pydantic
```

### Nếu dùng `python`:
```powershell
cd Source/ai/Multi_Agent/Source/Main/Service
python -m pip install flask flask-cors langchain langchain-ollama langgraph chromadb sentence-transformers python-dotenv pydantic
```

### Nếu dùng `python3`:
```powershell
cd Source/ai/Multi_Agent/Source/Main/Service
python3 -m pip install flask flask-cors langchain langchain-ollama langgraph chromadb sentence-transformers python-dotenv pydantic
```

## Chạy Flask API:

Sau khi cài đặt xong dependencies:

```powershell
# Dùng py
py flask_mas_api.py

# Hoặc dùng python
python flask_mas_api.py

# Hoặc dùng python3
python3 flask_mas_api.py
```

## Kiểm tra Python đã được cài đặt:

```powershell
# Thử các lệnh sau:
py --version
python --version
python3 --version
where python
where py
```

Nếu không có lệnh nào hoạt động, bạn cần cài đặt Python.

