-- Script để sửa lỗi foreign key constraint trong summary_sessions
-- Xóa các bản ghi có created_by không tồn tại trong bảng users

USE mydatabase;

-- Xóa các bản ghi summary_sessions có created_by không hợp lệ
DELETE FROM summary_sessions 
WHERE created_by IS NOT NULL 
AND created_by NOT IN (SELECT user_id FROM users);

-- Hoặc nếu muốn xóa tất cả summary_sessions có created_by NULL hoặc không hợp lệ:
-- DELETE FROM summary_sessions 
-- WHERE created_by IS NULL 
--    OR created_by NOT IN (SELECT user_id FROM users);

-- Sau khi dọn dữ liệu, foreign key constraint sẽ được tạo thành công khi khởi động lại ứng dụng
