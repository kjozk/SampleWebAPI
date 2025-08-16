from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from typing import Tuple
from database import get_db
from models.user import User
from jose import JWTError, jwt

import math

router = APIRouter()

# JWT設定（user_routes.pyと合わせる）
SECRET_KEY = "super-secret-change-this"
ALGORITHM = "HS256"

# JWT認証ユーティリティ
def get_current_user(token: str = Body(...), db: Session = Depends(get_db)) -> Tuple[User, dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="トークンが無効です")
    except JWTError:
        raise HTTPException(status_code=401, detail="トークンが無効です")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="ユーザーが存在しません")
    return user, payload

def make_response(success: bool, result=None, message: str = ""):
    return {"status": "success" if success else "error", "result": result, "message": message}

# --- ルート ---
@router.post("/add")
def add_numbers(a: float = Body(...), b: float = Body(...), token: str = Body(...), db: Session = Depends(get_db)):
    current_user, claims = get_current_user(token, db)

    if not claims.get("can_arithmetic", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="四則演算の権限がありません")

    return make_response(True, result=a + b)

@router.post("/sin")
def calculate_sin(x: float = Body(...), token: str = Body(...), db: Session = Depends(get_db)):
    current_user, claims = get_current_user(token, db)

    if not claims.get("can_trigonometry", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="三角関数の権限がありません")

    return make_response(True, result=math.sin(x))
