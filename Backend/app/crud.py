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
        full_name=user.full_name
    )
    
    # 3. Thêm đối tượng mới vào session và lưu vào DB
    db.add(db_user)
    db.commit()
    
    # 4. Refresh để lấy ID mới vừa được tạo
    db.refresh(db_user)
    
    return db_user

# TODO: Thêm các hàm CRUD khác ở đây
# ví dụ: get_accounts_by_user, create_transaction, ...