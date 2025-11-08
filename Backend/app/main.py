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



INTER_BANK_FEE = 0  # Phí 5,000 VND
MY_BANK_NAME = "TDTU_BANK"


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
def transfer_funds(
    transaction_request: schemas.TransactionCreate, 
    current_user: models.User = Depends(security.get_current_user), 
    db: Session = Depends(get_db)
):
    # 1. Xác thực PIN
    if not current_user.hashed_pin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng cài đặt mã PIN giao dịch trước")
    
    if not security.verify_password(transaction_request.pin, current_user.hashed_pin):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã PIN giao dịch không chính xác")

    # 2. Lấy tài khoản người gửi (Giả định 1 user 1 tài khoản)
    if not current_user.accounts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không có tài khoản ngân hàng")
    # Lấy ID của tài khoản gửi
    sender_account_id = current_user.accounts[0].id
    
    # Lấy lại đối tượng sender_account bằng session 'db' (Phiên 2)
    sender_account = db.query(models.Account).filter(models.Account.id == sender_account_id).first()
    if not sender_account:
        # Điều này không bao giờ nên xảy ra, nhưng để an toàn
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản người gửi")

    # 3. Lấy tài khoản người nhận
    # DÙNG HÀM MỚI: tìm theo SỐ TK và TÊN NGÂN HÀNG
    receiver_account = crud.get_account_by_number_and_bank(
        db, 
        account_number=transaction_request.receiver_account_number,
        bank_name=transaction_request.receiver_bank_name
    )

    if not receiver_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tài khoản người nhận không tồn tại hoặc sai ngân hàng")

    # 4. Kiểm tra tự chuyển tiền
    if sender_account.id == receiver_account.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể tự chuyển tiền cho chính mình")

    # 5. LOGIC TÍNH PHÍ (MỚI)
    amount_to_receive = transaction_request.amount # Số tiền người nhận nhận
    total_amount_to_debit = amount_to_receive   # Số tiền người gửi bị trừ
    fee = 0

    # Kiểm tra xem có phải liên ngân hàng không
    is_inter_bank = (sender_account.bank_name != receiver_account.bank_name)

    if is_inter_bank:
        fee = INTER_BANK_FEE
        total_amount_to_debit += fee

    # 6. Kiểm tra số dư với TỔNG SỐ TIỀN CẦN TRỪ
    if sender_account.balance < total_amount_to_debit:
        detail_msg = f"Số dư không đủ. Bạn cần {total_amount_to_debit} VND (đã bao gồm phí {fee} VND)"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_msg)

    # 7. Thực hiện giao dịch (DÙNG HÀM MỚI V2)
    db_transaction = crud.create_transaction_v2(
        db=db, 
        sender_account=sender_account, 
        receiver_account=receiver_account, 
        amount_to_receive=amount_to_receive,
        total_to_debit=total_amount_to_debit
    )
    
    if not db_transaction:
        # Lỗi này xảy ra nếu CSDL bị lỗi (đã check số dư ở trên)
        raise HTTPException(status_code=500, detail="Giao dịch thất bại do lỗi hệ thống")

    return db_transaction

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