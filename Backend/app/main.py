import smtplib, ssl # Thư viện gửi mail (dùng SSL)
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pydantic import BaseModel

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

load_dotenv() # Tải biến từ file .env
otp_storage = {} # Kho lưu OTP
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

# --- Endpoint 5: Chuyển tiền (Được bảo vệ) ---
@app.post("/api/transactions/transfer", response_model=schemas.Transaction)
def perform_transfer(
    transaction_request: schemas.TransactionCreate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    # API được bảo vệ đẻ thực hiện chuyển tiền
    
    # --- BƯỚC 1: XÁC THỰC MÃ PIN ---
    
    # 1a. Kiểm tra xem user đã tạo PIN chưa
    if not current_user.hashed_pin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Vui lòng tạo mã PIN giao dịch trước khi chuyển tiền"
        )

    # 1b. Xác thực PIN user nhập (từ 'transaction_request.pin')
    # với PIN đã lưu ('current_user.hashed_pin')
    # (dùng hàm 'verify_pin' bạn đã thêm trong 'security.py')
    if not security.verify_pin(transaction_request.pin, current_user.hashed_pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Mã PIN không chính xác"
        )
    
    # 2. Lấy tài khoản của người gửi
    # ( an toàn hơn, tránh lỗi [0])
    sender_accounts = crud.get_accounts_by_user(db, user_id=current_user.id)
    if not sender_accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User (sender) has no account",
        )
    sender_account = sender_accounts[0] # Lấy tài khoản đầu tiên

    # 3. Lấy tài khoản của người nhận
    receiver_account = crud.get_account_by_number(db, account_number=transaction_request.receiver_account_number)
    if not receiver_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver account not found",
        )
        
    # 4. Kiểm tra user tự chuyển cho chính mình
    if sender_account.id == receiver_account.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Cannot transfer to your own account",
        )
        
    # 5. Thực hiện giao dịch
    db_transaction = crud.create_transaction(
        db=db,
        sender_account=sender_account,
        receiver_account=receiver_account,
        amount=transaction_request.amount
    )
    
    # 6. Xử lí kết quả
    if db_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction failed (e.g., insufficient funds)",
        )
        
    # 7. Trả về 200 OK (Giao dịch thành công)
    return db_transaction

# --- Endpoint 6: Lấy Lịch sử Giao dịch (Được bảo vệ) ---
@app.get("/api/transactions/me", response_model=list[schemas.Transaction])
def read_user_transactions(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    API được bảo vệ, trả về TẤT CẢ giao dịch (gửi và nhận) của user hiện tại
    """
    # Chỉ cần gọi hàm crud để lấy giao dịch
    return crud.get_transactions_by_user(db, user_id=current_user.id)

@app.post("/api/pin/request-otp")
def request_pin_otp(current_user: models.User = Depends(security.get_current_user)):
    otp_code = str(random.randint(100000, 999999))
    expiry_time = datetime.now() + timedelta(minutes=5)
    otp_storage[current_user.username] = {"otp": otp_code, "expiry": expiry_time}

    # --- PHẦN GỬI EMAIL (Gmail) ---
    try:
        # Đọc thông tin từ file .env
        sender_email = os.getenv("EMAIL_SENDER")
        receiver_email = current_user.email # (Email thật của user)
        password = os.getenv("EMAIL_PASSWORD") # Mật khẩu 16 ký tự

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "Xac thuc Ma PIN - MyBank"
        body = f"Ma OTP cua ban la: {otp_code}. Ma se het han trong 5 phut."
        msg.attach(MIMEText(body, 'plain'))

        # Tạo kết nối SSL (an toàn)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")), context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

    except Exception as e:
        print(f"Lỗi gửi email: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống gửi email")
    # --- KẾT THÚC GỬI EMAIL ---

    return {"message": "OTP đã được gửi. Vui lòng kiểm tra email."}

class PinSetRequest(BaseModel):
    password: str # Mật khẩu đăng nhập
    otp: str
    new_pin: str # PIN mới (6 số)

@app.post("/api/pin/set")
def set_transaction_pin(
    request: PinSetRequest,
    auth_user: models.User = Depends(security.get_current_user), 
    db: Session = Depends(get_db)
):
    # 1. Xác thực mật khẩu đăng nhập
    if not security.verify_password(request.password, auth_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu")

    # 2. Xác thực OTP
    stored_otp = otp_storage.get(auth_user.username)
    if not stored_otp or datetime.now() > stored_otp["expiry"] or stored_otp["otp"] != request.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP sai hoặc hết hạn")

    # 3. Lấy user MỘT LẦN NỮA, nhưng dùng session 'db' (Session 10)
    # Điều này đảm bảo 'db_user' được đính kèm vào đúng session
    db_user = db.query(models.User).filter(models.User.id == auth_user.id).first()
    if not db_user:
        # Điều này không bao giờ nên xảy ra, nhưng để an toàn
        raise HTTPException(status_code=404, detail="User not found in session")
    
    # 4. Hash và lưu PIN mới
    db_user.hashed_pin = security.get_pin_hash(request.new_pin)
    # db.add(db_user) # KHÔNG cần 'add' vì 'db_user' đã được lấy từ 'db'
    db.commit() # Chỉ cần commit session 'db'

    del otp_storage[auth_user.username] # Xóa OTP đã dùng
    return {"message": "Tạo mã PIN thành công!"}