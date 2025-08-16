from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DB URL（SQLiteの例）
DATABASE_URL = "sqlite:///./app.db"

# エンジン作成
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # SQLite用
)

# セッション作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()

# 依存関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
