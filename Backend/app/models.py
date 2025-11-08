from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func 
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(50), default="CUSTOMER")
    accounts = relationship("Account", back_populates="owner")
    hashed_pin = Column(String(255), nullable=True) # PIN 6 số (đã hash)
    
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, index=True, nullable=False)
    balance = Column(Integer, nullable=False, default=0) # Số dư (lưu bằng Int)
    
    # Tạo khóa ngoại (Foreign Key)
    # Nó liên kết cột 'owner_id' này với cột 'id' của bảng 'users'
    owner_id = Column(Integer, ForeignKey("users.id"))

    # ngân hàng tạo ra mặc định là TDTU_BANK
    bank_name = Column(String(50), nullable=False, default="TDTU_BANK")

    # Tạo khóa ngoại (Foreign Key)


    # Tạo mối quan hệ "ngược"
    # Giúp ta gọi `user.accounts` để lấy danh sách tài khoản
    owner = relationship("User", back_populates="accounts")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    
    # Ghi lại thời gian tạo (tự động)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # ID tài khoản gửi (Foreign Key tới 'accounts')
    sender_id = Column(Integer, ForeignKey("accounts.id"))
    # ID tài khoản nhận (Foreign Key tới 'accounts')
    receiver_id = Column(Integer, ForeignKey("accounts.id"))
    
    # (Tùy chọn, không bắt buộc) Tạo quan hệ ngược
    # sender = relationship("Account", foreign_keys=[sender_id])
    # receiver = relationship("Account", foreign_keys=[receiver_id])
    