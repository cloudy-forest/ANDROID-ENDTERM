from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .models import User as ModelUser # Đổi tên để tránh xung đột

# Import tất cả các module bạn vừa tạo
from . import crud, models, schemas, security
from .database import SessionLocal, engine, Base

# -------------------------------------------------------------------
# !!! QUAN TRỌNG !!!
# Dòng này ra lệnh cho SQLAlchemy tạo tất cả các bảng (định nghĩa
# trong models.py) vào database MySQL.
# Nó sẽ kiểm tra xem bảng đã tồn tại chưa, nếu chưa, nó sẽ tạo.
Base.metadata.create_all(bind=engine)
# -------------------------------------------------------------------

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# --- Dependency (Phần phụ thuộc) ---
# Đây là một "dependency" của FastAPI.
# Nó sẽ tạo một phiên (session) database mới cho mỗi request,
# tự động đóng lại sau khi request hoàn tất.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === API ENDPOINTS ===

@app.get("/")
def read_root():
    return {"message": "Chào mừng bạn đến với Mobile Banking API!"}

# --- Endpoint 1: Đăng Ký (Register) ---
@app.post("/api/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Kiểm tra xem user đã tồn tại chưa
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        # Nếu đã tồn tại, báo lỗi 400
        raise HTTPException(status_code=400, detail="Username đã tồn tại")
    
    # 2. Nếu chưa, tạo user mới (gọi hàm từ crud.py)
    return crud.create_user(db=db, user=user)

# --- Endpoint 2: Đăng Nhập (Login) ---
# Đây chính là API mà Android sẽ gọi
@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(login_request: schemas.LoginRequest, db: Session = Depends(get_db)):
    
    # 1. Lấy user từ DB (gọi hàm từ crud.py)
    user = crud.get_user_by_username(db, username=login_request.username)
    
    # 2. Kiểm tra user có tồn tại VÀ mật khẩu có đúng không
    # (gọi hàm verify_password từ security.py)
    if not user or not security.verify_password(login_request.password, user.hashed_password):
        # Nếu sai, báo lỗi 401 Unauthorized
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"}, # Header chuẩn cho lỗi 401
        )
    
    # 3. Nếu đúng, tạo JWT Token (gọi hàm từ security.py)
    access_token = security.create_access_token(
        data={"sub": user.username} # "sub" (subject) là tên user
    )
    
    # 4. Trả về token cho client (Android)
    # FastAPI sẽ tự động chuyển nó thành JSON: {"token": "..."}
    # khớp với `LoginResponse.java`
    return {"token": access_token}

# --- Endpoint 3: Lấy thông tin User (Được bảo vệ) ---
@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(current_user: ModelUser = Depends(security.get_current_user)):
    
    # API này được bảo vệ. 
    # Nó dùng dependency 'get_current_user' từ 'security.py'.
    # FastAPI sẽ tự động chạy 'get_current_user' trước.
    # - Nếu token hợp lệ, 'get_current_user' sẽ trả về user.
    # - Nếu token sai/thiếu, nó sẽ tự động trả về lỗi 401.
    
    # Nếu code chạy được đến đây, nghĩa là token đã hợp lệ.
    # Chỉ cần trả về user là xong.
    return current_user

# --- Endpoint 4: Lấy tài khoản (Được bảo vệ) ---
@app.get("/api/accounts/me", response_model=list[schemas.Account])
def read_user_accounts(current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    """
    API được bảo vệ, trả về TẤT CẢ tài khoản của user hiện tại
    """
    # Lấy tài khoản từ DB
    accounts = crud.get_accounts_by_user(db, user_id=current_user.id)
    return accounts