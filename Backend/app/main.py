from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

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