# Import với xử lý lỗi
try:
    from plantuml import PlantUML
    HAS_PLANTUML = True
except ImportError:
    HAS_PLANTUML = False
    print("Thư viện 'plantuml' chưa được cài đặt. Sử dụng phương án dự phòng với requests.")

try:
    from IPython.display import Image, display
    HAS_IPYTHON = True
except ImportError:
    HAS_IPYTHON = False
    print("Không có IPython. Sẽ hiển thị URL thay vì ảnh.")

import requests
import zlib
import base64

uml_code = """
@startuml
title Sequence Diagram - Admin Management System

actor Admin
participant SummaryController
participant UserController
participant ConversationController
participant TagController
database Database

'=== Quản lý Summary ===
Admin -> SummaryController: GET /api/summaries/admin
SummaryController -> Database: Lấy danh sách summaries
Database --> SummaryController: Danh sách SummaryAdminDTO
SummaryController --> Admin: Danh sách summaries với thông tin admin

Admin -> SummaryController: GET /api/summaries/status/PENDING
SummaryController -> Database: Lọc summaries theo status
Database --> SummaryController: Danh sách summaries PENDING
SummaryController --> Admin: Danh sách summaries cần duyệt

alt Duyệt Summary
    Admin -> SummaryController: PUT /api/summaries/{id}/status\n(status: APPROVED)
    SummaryController -> Database: Cập nhật status summary
    Database --> SummaryController: Summary đã được cập nhật
    SummaryController --> Admin: Xác nhận duyệt thành công
else Từ chối Summary
    Admin -> SummaryController: PUT /api/summaries/{id}/status\n(status: REJECTED)
    SummaryController -> Database: Cập nhật status summary
    Database --> SummaryController: Summary đã được cập nhật
    SummaryController --> Admin: Xác nhận từ chối thành công
end

alt Xóa một Summary
    Admin -> SummaryController: DELETE /api/summaries/{id}
    SummaryController -> Database: Xóa summary
    Database --> SummaryController: Xác nhận xóa
    SummaryController --> Admin: Xác nhận xóa thành công
else Xóa nhiều Summary
    Admin -> SummaryController: DELETE /api/summaries/bulk\n(ids: [id1, id2, ...])
    SummaryController -> Database: Xóa nhiều summaries
    Database --> SummaryController: Xác nhận xóa
    SummaryController --> Admin: Xác nhận xóa thành công
end

'=== Quản lý User ===
Admin -> UserController: GET /api/users
UserController -> Database: Lấy danh sách users
Database --> UserController: Danh sách users
UserController --> Admin: Danh sách tất cả users

Admin -> UserController: GET /api/users/role/CONTRIBUTOR
UserController -> Database: Lọc users theo role
Database --> UserController: Danh sách users CONTRIBUTOR
UserController --> Admin: Danh sách contributors

alt Tạo User mới
    Admin -> UserController: POST /api/users\n(user data)
    UserController -> Database: Tạo user mới
    Database --> UserController: User đã được tạo
    UserController --> Admin: User mới đã tạo
else Cập nhật User
    Admin -> UserController: PUT /api/users/{id}\n(user data)
    UserController -> Database: Cập nhật user
    Database --> UserController: User đã được cập nhật
    UserController --> Admin: User đã được cập nhật
else Xóa User
    Admin -> UserController: DELETE /api/users/{id}
    UserController -> Database: Xóa user
    Database --> UserController: Xác nhận xóa
    UserController --> Admin: Xác nhận xóa user thành công
end

'=== Quản lý Conversation ===
Admin -> ConversationController: GET /api/conversations
ConversationController -> Database: Lấy danh sách conversations
Database --> ConversationController: Danh sách conversations
ConversationController --> Admin: Danh sách tất cả conversations

Admin -> ConversationController: DELETE /api/conversations/{conversation_id}
ConversationController -> Database: Xóa conversation
Database --> ConversationController: Xác nhận xóa
ConversationController --> Admin: Xác nhận xóa conversation thành công

'=== Quản lý Tag ===
Admin -> TagController: GET /api/tags
TagController -> Database: Lấy danh sách tags
Database --> TagController: Danh sách tags
TagController --> Admin: Danh sách tất cả tags

alt Tạo Tag mới
    Admin -> TagController: POST /api/tags\n(tag data)
    TagController -> Database: Tạo tag mới
    Database --> TagController: Tag đã được tạo
    TagController --> Admin: Tag mới đã tạo
else Xóa Tag
    Admin -> TagController: DELETE /api/tags/{id}
    TagController -> Database: Xóa tag
    Database --> TagController: Xác nhận xóa
    TagController --> Admin: Xác nhận xóa tag thành công
end

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
    # Phương án dự phòng: Sử dụng URL trực tiếp với encode
    import urllib.parse
    import zlib
    import base64
    import requests
    
    try:
        # Encode PlantUML code thành URL-safe base64 (PlantUML encoding)
        compressed = zlib.compress(uml_code.encode('utf-8'), level=9)
        encoded = base64.b64encode(compressed).decode('utf-8')
        # Thay thế các ký tự không URL-safe theo chuẩn PlantUML
        encoded = encoded.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=', 
                                                    '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'))
        
        # URL PlantUML server
        plantuml_url = f"http://www.plantuml.com/plantuml/png/{encoded}"
        
        print(f"Lỗi khi sử dụng PlantUML library: {str(e)}")
        print(f"\nĐang thử phương án dự phòng...")
        
        # Thử tải ảnh từ URL
        response = requests.get(plantuml_url, timeout=10)
        if response.status_code == 200:
            display(Image(response.content))
            print("✓ Đã tải diagram thành công từ URL!")
        else:
            print(f"Không thể tải ảnh từ URL. Status code: {response.status_code}")
            print(f"\nVui lòng mở URL sau trong trình duyệt để xem diagram:")
            print(plantuml_url)
    except Exception as e2:
        print(f"Lỗi khi sử dụng phương án dự phòng: {str(e2)}")
        print(f"\nLỗi ban đầu: {str(e)}")
        print("\nVui lòng kiểm tra kết nối internet hoặc thử lại sau.")

