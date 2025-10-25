from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(50), default="CUSTOMER")
    accounts = relationship("Account", back_populates="owner")
    
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, index=True, nullable=False)
    balance = Column(Integer, nullable=False, default=0) # Số dư (lưu bằng Int)
    
    # Tạo khóa ngoại (Foreign Key)
    # Nó liên kết cột 'owner_id' này với cột 'id' của bảng 'users'
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Tạo mối quan hệ "ngược"
    # Giúp ta gọi `user.accounts` để lấy danh sách tài khoản
    owner = relationship("User", back_populates="accounts")

