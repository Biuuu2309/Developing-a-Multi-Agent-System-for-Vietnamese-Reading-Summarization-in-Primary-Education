# Cách Activate Conda trong PowerShell

## Vấn đề: Conda không được nhận diện trong PowerShell

Có 2 cách giải quyết:

## Cách 1: Khởi tạo Conda trong PowerShell (Một lần duy nhất)

### Bước 1: Tìm đường dẫn Conda

Thử các đường dẫn sau (thay `minhv` bằng tên user của bạn):

```powershell
# Kiểm tra các vị trí thường gặp
Test-Path "$env:USERPROFILE\anaconda3\Scripts\conda.exe"
Test-Path "$env:USERPROFILE\miniconda3\Scripts\conda.exe"
Test-Path "C:\ProgramData\anaconda3\Scripts\conda.exe"
Test-Path "C:\ProgramData\miniconda3\Scripts\conda.exe"
```

### Bước 2: Khởi tạo Conda

Sau khi tìm thấy đường dẫn, chạy (thay đường dẫn cho đúng):

```powershell
# Ví dụ nếu conda ở C:\Users\minhv\anaconda3
& "C:\Users\minhv\anaconda3\Scripts\conda.exe" init powershell
```

### Bước 3: Restart PowerShell

- Đóng PowerShell hiện tại
- Mở PowerShell mới
- Chạy: `conda activate pytorch-env`

## Cách 2: Dùng Anaconda Prompt (Đơn giản nhất)

### Bước 1: Mở Anaconda Prompt
- Từ Start Menu, tìm "Anaconda Prompt" hoặc "Anaconda PowerShell Prompt"
- Mở nó

### Bước 2: Activate environment và chạy

```bash
# Activate environment
conda activate pytorch-env

# Di chuyển đến thư mục
cd E:\Project_NguyenMinhVu_2211110063\Source\ai\Multi_Agent\Source\Main\Service

# Cài đặt dependencies (nếu chưa có)
pip install -r requirements.txt

# Chạy Flask API
python flask_mas_api.py
```

## Cách 3: Activate thủ công trong PowerShell hiện tại

Nếu bạn biết đường dẫn conda, có thể activate thủ công:

```powershell
# Thay đường dẫn cho đúng với máy bạn
$condaPath = "C:\Users\minhv\anaconda3\Scripts\activate.bat"
& $condaPath pytorch-env

# Hoặc nếu dùng miniconda
$condaPath = "C:\Users\minhv\miniconda3\Scripts\activate.bat"
& $condaPath pytorch-env
```

Sau đó chạy:
```powershell
cd E:\Project_NguyenMinhVu_2211110063\Source\ai\Multi_Agent\Source\Main\Service
python flask_mas_api.py
```

## Cách 4: Tạo script để chạy nhanh

Tạo file `run_flask_api.bat` trong thư mục Service:

```batch
@echo off
call C:\Users\minhv\anaconda3\Scripts\activate.bat pytorch-env
cd /d E:\Project_NguyenMinhVu_2211110063\Source\ai\Multi_Agent\Source\Main\Service
python flask_mas_api.py
pause
```

Sau đó double-click file `.bat` để chạy.

## Kiểm tra Conda đã được activate chưa

Sau khi activate, bạn sẽ thấy `(pytorch-env)` ở đầu dòng prompt:

```powershell
(pytorch-env) PS E:\Project_NguyenMinhVu_2211110063\Source\ai\Multi_Agent\Source\Main\Service>
```

Nếu thấy `(pytorch-env)` là đã activate thành công!

## Quick Start (Khuyến nghị)

**Dùng Anaconda Prompt** - Đơn giản nhất:

1. Mở "Anaconda Prompt" từ Start Menu
2. Chạy:
```bash
conda activate pytorch-env
cd E:\Project_NguyenMinhVu_2211110063\Source\ai\Multi_Agent\Source\Main\Service
pip install -r requirements.txt
python flask_mas_api.py
```

