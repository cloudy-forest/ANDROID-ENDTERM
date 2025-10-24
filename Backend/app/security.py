from passlib.context import CryptContext
from jose import JWTError
from jose import jwt
from datetime import datetime, timedelta

# --- 1. Cấu hình Mật khẩu ---

# Khởi tạo CryptContext, chỉ định dùng thuật toán "bcrypt"
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    So sánh mật khẩu gốc (plain) với mật khẩu đã mã hóa (hashed)
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Mã hóa một mật khẩu gốc
    """
    return pwd_context.hash(password)


# --- 2. Cấu hình JWT Token ---

# QUAN TRỌNG: Đây là "khóa bí mật" để tạo token.
# Hãy thay bằng một chuỗi ngẫu nhiên, phức tạp của riêng bạn.
# Bạn có thể tự tạo 1 chuỗi bằng cách vào Python gõ:
# >>> import secrets
# >>> secrets.token_hex(32)
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token sẽ hết hạn sau 30 phút

def create_access_token(data: dict):
    """
    Tạo JWT access token dựa trên dữ liệu đầu vào (data)
    """
    to_encode = data.copy()
    
    # Thêm thời gian hết hạn vào token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Mã hóa token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt