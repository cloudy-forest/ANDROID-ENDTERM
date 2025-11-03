from pydantic import BaseModel # BaseModel của Pydantic
from datetime import datetime
# Schemas cho User
# --------------------

# Đây là dữ liệu client (Android) gửi lên khi đăng ký
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str

# Đây là dữ liệu trả về cho client khi xem thông tin user
# (Nó không chứa 'hashed_password' để đảm bảo an toàn)
class User(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

    class Config:
        from_attributes = True


# Schemas cho Authentication
# --------------------

# Đây là dữ liệu client (Android) gửi lên khi đăng nhập
# (Khớp với LoginRequest.java)
class LoginRequest(BaseModel):
    username: str
    password: str

# Đây là dữ liệu server trả về khi login thành công
# (Khớp với LoginResponse.java)
class Token(BaseModel):
    token: str
    token_type: str = "bearer" # Giá trị mặc định
    
# --- Schemas cho Account ---

class AccountBase(BaseModel):
    account_number: str
    balance: int

class Account(AccountBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True # Đổi từ orm_mode
        
# Cập nhật lại schema 'User' (quan trọng)
# Để nó có thể hiển thị danh sách tài khoản khi cần
class User(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    accounts: list[Account] = [] # Thêm dòng này

    class Config:
        from_attributes = True
        

# ---Schemas cho Transaction----
class TransactionBase(BaseModel):
    amount: int
    
# schemas để nhận request: Cần biết số tài khoản nhận
class TransactionCreate(TransactionBase):
    receiver_account_number: str # User sẽ nhập số tài khoản này
    pin: str # Yêu cầu mã pin
    
# schemas để trả về (hiển thị lịch sử)
class Transaction(TransactionBase):
    id: int
    timestamp: datetime
    sender_id: int
    receiver_id: int
    
    class Config:
        from_attributes = True
