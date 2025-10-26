-- ----------------------------------------------------
-- Script thêm tài khoản cho user 'thuyvan'
-- (Script này an toàn để chạy nhiều lần, 
--  nó sẽ không tạo trùng tài khoản)
-- ----------------------------------------------------

-- 1. Tìm ID của user 'thuyvan' và lưu vào biến @user_id
-- (Đảm bảo bạn đã TẠO user 'thuyvan' qua API /register trước)
SELECT id INTO @user_id FROM users WHERE username = 'thuyvan' LIMIT 1;

-- 2. Chèn tài khoản Tiết kiệm (50 triệu) NẾU nó chưa tồn tại
INSERT INTO accounts (account_number, balance, owner_id)
SELECT * FROM (SELECT '111222333' AS account_number, 50000000 AS balance, @user_id AS owner_id) AS temp
WHERE NOT EXISTS (
    SELECT 1 FROM accounts WHERE account_number = '111222333'
) LIMIT 1;

-- 3. Chèn tài khoản Thanh toán (2 triệu) NẾU nó chưa tồn tại
INSERT INTO accounts (account_number, balance, owner_id)
SELECT * FROM (SELECT '999888777' AS account_number, 2000000 AS balance, @user_id AS owner_id) AS temp
WHERE NOT EXISTS (
    SELECT 1 FROM accounts WHERE account_number = '999888777'
) LIMIT 1;