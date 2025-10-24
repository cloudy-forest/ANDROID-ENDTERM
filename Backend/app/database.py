from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL kết nối: "mysql+driver://user:password@host:port/dbname"
# Chúng ta kết nối tới "localhost:3306" vì docker-compose đã
# "mở" cổng 3306 của container ra máy thật của bạn.
DATABASE_URL = "mysql+pymysql://myuser:mypassword@localhost:3306/banking_app"

# Tạo "engine" (trình điều khiển) chính của SQLAlchemy
engine = create_engine(DATABASE_URL)

# Tạo một "SessionLocal" class
# Mỗi instance của class này sẽ là một phiên làm việc (session) với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo một class Base.
# Tất cả các model (bảng) của chúng ta sẽ kế thừa từ class này.
Base = declarative_base()