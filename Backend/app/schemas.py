from pydantic import BaseModel
from datetime import datetime

# -------------------------------------------------------------------
# !!! Sửa lỗi: Di chuyển Account lên TRƯỚC User
# để class User có thể tham chiếu đến 'list[Account]'
# -------------------------------------------------------------------

# --- Schemas cho Account ---
class AccountBase(BaseModel):
    account_number: str
    balance: int

class Account(AccountBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# -------------------------------------------------------------------
# !!! Sửa lỗi: Hợp nhất 2 class User và thêm 'email'
# -------------------------------------------------------------------

# --- Schemas cho User ---

# Tạo một class Base để chứa các trường chung
class UserBase(BaseModel):
    username: str
    full_name: str | None = None
    email: str  

# Dữ liệu client gửi lên khi ĐĂNG KÝ
class UserCreate(UserBase): # <-- Kế thừa từ UserBase
    password: str

# Dữ liệu trả về cho client (HỢP NHẤT TỪ 2 CLASS CŨ)
class User(UserBase): # <-- Kế thừa từ UserBase
    id: int
    role: str
    accounts: list[Account] = [] # Giữ lại danh sách tài khoản

    class Config:
        from_attributes = True

# --- Schemas cho Authentication ---
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    token: str
    token_type: str = "bearer"

# --- Schemas cho Transaction ---
class TransactionBase(BaseModel):
    amount: int
    
class TransactionCreate(TransactionBase):
    receiver_account_number: str
    pin: str
    
class Transaction(TransactionBase):
    id: int
    timestamp: datetime
    sender_id: int
    receiver_id: int
    
    class Config:
        from_attributes = True