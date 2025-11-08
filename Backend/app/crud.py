from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas, security

# --- READ ---
def get_user_by_username(db: Session, username: str):
    """
    Hàm READ: Lấy user bằng username
    """
    return db.query(models.User).filter(models.User.username == username).first()


# --- CREATE ---
def create_user(db: Session, user: schemas.UserCreate):
    """
    Hàm CREATE: Tạo user mới
    """
    # 1. Mã hóa mật khẩu của user trước khi lưu
    hashed_password = security.get_password_hash(user.password)
    
    # 2. Tạo một đối tượng 'User' (của model) từ dữ liệu
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        email=user.email,
        role="user"
    )
    
    # 3. Thêm đối tượng mới vào session và lưu vào DB
    db.add(db_user)
    db.commit()
    
    # 4. Refresh để lấy ID mới vừa được tạo
    db.refresh(db_user)
    
    return db_user

# --- CRUD cho Account ---

def get_accounts_by_user(db: Session, user_id: int):
    """
    Lấy tất cả tài khoản của một user
    """
    return db.query(models.Account).filter(models.Account.owner_id == user_id).all()

# Hàm helper để lấy tài khoản bằng SỐ TÀI KHOẢN
def get_account_by_number(db: Session, account_number: str):
    return db.query(models.Account).filter(models.Account.account_number == account_number).first()

# --- HÀM CHUYỂN TIỀN---
def create_transaction(db: Session, sender_account: models.Account, receiver_account: models.Account, amount: int):

    # 1. Kiểm tra số dư
    if sender_account.balance < amount:
        # Nếu không đủ tiền, trả về False(thất bại)
        return None
    try: 
        # 2. Trừ tiền người gửi 
        sender_account.balance -= amount
        
        # 3. Cộng tiền người nhận
        receiver_account.balance += amount
        
        # 4. Tạo bản ghi (record) giao dịch
        db_transaction = models.Transaction(
            amount=amount,
            sender_id=sender_account.id,
            receiver_id=receiver_account.id
        )
        
        # 5. Thêm cả 3 thay đổi (sender, receiver, transaction) vào session
        db.add(sender_account)
        db.add(receiver_account)
        db.add(db_transaction)
        
        # 6. Commit (Lưu) tất cả thay đổi vào db
        # Đây là một "giao dịch" (database transaction):
        # Hoặc tất cả cùng thành công, hoặc không gì cả 
        db.commit()
        
        # 7 Trả về bản ghi giao dịch
        return  db_transaction
    
    except Exception as e: 
        # Nếu có lỗi, hủy mọi thay đổi
        db.rollback()
        return None
    
def get_transactions_by_user(db: Session, user_id: int):
    """
    Lấy tất cả giao dịch (gửi và nhận) của 1 user sắp xếp theo thời gian mới nhất
    """
    # Truy vấn các tài khoản của user
    # 1. Lấy tất cả ID tài khoản của user này
    user_accounts = db.query(models.Account.id).filter(models.Account.owner_id == user_id).all()
    # Chuyển [[1], [2]] thành [1, 2]
    account_ids = [account.id for account in user_accounts]
    
    if not account_ids:
        # Nếu user không có tài khoản nào, họ không có giao dịch
        return []
    
    # 2. Tìm tất cả giao dịch
    #    nơi người gửi (sender_id) LÀ MỘT TRONG CÁC tài khoản của user
    #    HOẶC người nhận (receiver_id) LÀ MỘT TRONG CÁC tài khoản của user
    transactions = db.query(models.Transaction).filter(
        or_(
            models.Transaction.sender_id.in_(account_ids),
            models.Transaction.receiver_id.in_(account_ids)
        )
    ).order_by(models.Transaction.timestamp.desc()).all() # Sắp xếp mới nhất lên đầu
    
    return transactions

    
# TODO: Thêm các hàm CRUD khác ở đây

