from sqlalchemy.orm import Session
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

def get_account_by_number_and_bank(db: Session, account_number: str, bank_name: str):
    """
    Tìm tài khoản bằng SỐ TK và TÊN NGÂN HÀNG
    """
    return db.query(models.Account).filter(
        models.Account.account_number == account_number,
        models.Account.bank_name == bank_name
    ).first()

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
    
def create_transaction_v2(db: Session, sender_account: models.Account, receiver_account: models.Account, amount_to_receive: int, total_to_debit: int):
    """
    Hàm chuyển tiền V2:
    - amount_to_receive: Số tiền người nhận nhận được
    - total_to_debit: Tổng số tiền người gửi bị trừ (đã bao gồm phí)
    """

    # 1. Kiểm tra số dư (với tổng số tiền bị trừ)
    if sender_account.balance < total_to_debit:
        return None # Không đủ tiền
    try: 
        # 2. Trừ tiền người gửi (Trừ tổng số tiền)
        sender_account.balance -= total_to_debit
        
        # 3. Cộng tiền người nhận (Chỉ cộng số tiền gốc)
        receiver_account.balance += amount_to_receive
        
        # 4. Tạo bản ghi (record) giao dịch
        db_transaction = models.Transaction(
            amount=amount_to_receive, # Ghi lại số tiền gốc
            sender_id=sender_account.id,
            receiver_id=receiver_account.id
            # Bạn có thể thêm cột 'fee' vào model Transaction nếu muốn
        )
        
        # 5. Thêm cả 3 thay đổi vào session
        db.add(sender_account)
        db.add(receiver_account)
        db.add(db_transaction)
        
        # 6. Commit (Lưu)
        db.commit()
        
        # 7. Refresh
        db.refresh(db_transaction)
        db.refresh(sender_account)
        db.refresh(receiver_account)
        
        return db_transaction

    except Exception as e:
        # 7. ... hoặc Rollback (Hoàn tác) nếu có lỗi
        print(f"Lỗi giao dịch: {e}")
        db.rollback()
        return None
    
# TODO: Thêm các hàm CRUD khác ở đây

