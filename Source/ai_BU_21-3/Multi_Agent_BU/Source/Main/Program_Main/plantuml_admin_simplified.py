from plantuml import PlantUML
from IPython.display import Image, display
import requests
import zlib
import base64

uml_code = """
@startuml
title Sequence Diagram - Admin Management System (Simplified)

actor Admin
participant SummaryController
participant UserController
participant ConversationController
participant TagController
database Database

'=== Quản lý Summary ===
Admin -> SummaryController: GET /api/summaries/admin
SummaryController -> Database: Lấy danh sách summaries
Database --> Admin: Danh sách summaries

alt Duyệt/Từ chối Summary
    Admin -> SummaryController: PUT /api/summaries/{id}/status
    SummaryController -> Database: Cập nhật status
    Database --> Admin: Xác nhận thành công
else Xóa Summary
    Admin -> SummaryController: DELETE /api/summaries/{id}
    SummaryController -> Database: Xóa summary
    Database --> Admin: Xác nhận xóa
end

'=== Quản lý User ===
Admin -> UserController: GET /api/users
UserController -> Database: Lấy danh sách users
Database --> Admin: Danh sách users

alt Tạo/Cập nhật/Xóa User
    Admin -> UserController: POST/PUT/DELETE /api/users/{id}
    UserController -> Database: Thao tác với user
    Database --> Admin: Kết quả thao tác
end

'=== Quản lý Conversation & Tag ===
Admin -> ConversationController: GET /api/conversations
ConversationController -> Database: Lấy danh sách
Database --> Admin: Danh sách conversations

Admin -> TagController: GET /api/tags
TagController -> Database: Lấy danh sách tags
Database --> Admin: Danh sách tags

alt Xóa/Tạo Conversation hoặc Tag
    Admin -> ConversationController/TagController: DELETE/POST
    Controller -> Database: Thao tác
    Database --> Admin: Xác nhận
end

'--- Điểm kết thúc quy trình ---
Admin -> Database: Lưu log hoạt động quản trị
Database --> Admin: Xác nhận hoàn tất

@enduml
"""

# Kết nối đến PlantUML server công khai
try:
    server = PlantUML(url="http://www.plantuml.com/plantuml/png/")
    # Gửi UML code đến server và nhận dữ liệu hình ảnh
    image_data = server.processes(uml_code)
    # Hiển thị ảnh UML trực tiếp trong Jupyter Notebook
    display(Image(image_data))
except Exception as e:
    # Phương án dự phòng: Encode và gọi URL trực tiếp
    try:
        compressed = zlib.compress(uml_code.encode('utf-8'), level=9)
        encoded = base64.b64encode(compressed).decode('utf-8')
        # PlantUML encoding: A-Z -> 0-9, a-z -> A-Z, 0-9 -> a-z, + -> -, / -> _
        # Loại bỏ '=' padding trước khi translate
        encoded = encoded.rstrip('=')
        encoded = encoded.translate(str.maketrans(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
            '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        ))
        
        plantuml_url = f"http://www.plantuml.com/plantuml/png/{encoded}"
        print(f"Lỗi PlantUML library: {str(e)}")
        print("Đang thử phương án dự phòng...")
        
        response = requests.get(plantuml_url, timeout=10)
        if response.status_code == 200:
            display(Image(response.content))
            print("✓ Đã tải diagram thành công!")
        else:
            print(f"Status code: {response.status_code}")
            print(f"\nURL PlantUML:\n{plantuml_url}")
    except Exception as e2:
        print(f"Lỗi phương án dự phòng: {str(e2)}")
        print(f"\nLỗi ban đầu: {str(e)}")

