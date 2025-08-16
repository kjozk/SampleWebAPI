from sqlalchemy import Column, Integer, String, Boolean
from passlib.context import CryptContext
from database import Base  # ← database.py の Base を使う

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    is_admin = Column(Boolean, default=False)
    can_arithmetic = Column(Boolean, default=False)
    can_trigonometry = Column(Boolean, default=False)
    can_logarithm = Column(Boolean, default=False)

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    @property
    def permissions(self) -> dict:
        """ユーザーの権限を辞書で返す"""
        return {
            "can_arithmetic": self.can_arithmetic,
            "can_trigonometry": self.can_trigonometry,
            "can_logarithm": self.can_logarithm,
            "is_admin": self.is_admin
        }

    def granted_permissions(self) -> list:
        """True の権限だけをリストで返す"""
        return [k for k, v in self.permissions.items() if v]
    