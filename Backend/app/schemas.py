from pydantic import BaseModel

# BaseModel của Pydantic

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