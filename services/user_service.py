from sqlalchemy.orm import Session
from models.user import User
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import SessionLocal

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class UserService:

    @staticmethod
    def create_user(db: Session, username: str, password: str):
        if db.query(User).filter(User.username == username).first():
            return False, "ユーザー名は既に存在します"
        
        user = User(username=username)
        user.can_arithmetic = True
        user.can_trigonometry = False
        user.set_password(password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return True, "登録成功"

    @staticmethod
    def authenticate(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            return True, user
        return False, None

    @staticmethod
    def change_password(db: Session, username: str, old_pw: str, new_pw: str):
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.check_password(old_pw):
            return False, "旧パスワードが違います"
        user.set_password(new_pw)
        db.commit()
        return True, "パスワード変更成功"

    @staticmethod
    def delete_user(db: Session, username: str):
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False, "ユーザーが存在しません"
        db.delete(user)
        db.commit()
        return True, f"ユーザー {username} を削除しました"

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return token

    @staticmethod
    def verify_access_token(token: str):
        try:
            # 認証
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # ユーザー名を取得
            username = payload.get("username")
            if not username:
                return False, None

            # DB からユーザー取得
            db: Session = SessionLocal()
            try:
                user = db.query(User).filter(User.username == username).first()
            finally:
                db.close()

            if not user:
                return False, None

            # ユーザー情報を返す
            return True, user

        except JWTError:
            return False, None
