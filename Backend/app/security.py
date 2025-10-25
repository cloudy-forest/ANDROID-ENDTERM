from passlib.context import CryptContext
from jose import JWTError
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import crud, database 
from sqlalchemy.orm import Session 

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

ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token sẽ hết hạn sau 30 phút

# Cấu hình OAuth2: báo cho FastAPI biết "tokenUrl" là gì
# Android sẽ không dùng cái này, nhưng dependency của FastAPI cần nó
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Hàm Dependency để lấy DB
# cần hàm này vì không thể import ngược từ main.py
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Hàm quan trọng nhất
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Dependency này sẽ: 
    # 1. Lấy token từ header "Authorization" của request
    # 2. Giải mã token
    # 3. Lấy username từ token
    # 4. Lấy user từ database và trả về
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Giải mã JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: string = payload.get("sub") # "sub" là username đã set lúc tạo token
        if username is None:
            raise credentials_exception
    except JWTError:
        # Nếu token sai, báo lỗi 
        raise credentials_exception
    
    # Lấy user từ DB
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        # Nếu user không tồn tại, báo lỗi
        raise credentials_exception
    
    # Trả về đối tượng user (của SQLAlchemy)
    return user