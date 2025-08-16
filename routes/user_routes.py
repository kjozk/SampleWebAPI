from fastapi import APIRouter, HTTPException, Request, Depends, Form, Body, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import UserService
from models.user import User
from models.auth_request import AuthRequest
from jose import JWTError, jwt
from datetime import datetime, timedelta

router = APIRouter()

# JWT設定
SECRET_KEY = "super-secret-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

templates = Jinja2Templates(directory="templates")  # HTMLテンプレートの格納フォルダ


@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    messages = []  # ここで必要ならメッセージを追加
    return templates.TemplateResponse(
        "login.html", {"request": request, "messages": messages}
    )

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- 認証ユーティリティ ---
def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="トークンが必要です")
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


def make_response(success: bool, message: str, data=None):
    return {
        "status": "success" if success else "error",
        "message": message,
        "data": data,
    }


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    # ユーザー作成フォームを表示
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db),
):
    if password != password2:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "パスワードが一致しません",
                "username": username,
            },
        )

    ok, msg = UserService.create_user(db, username, password)
    if not ok:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": msg, "username": username}
        )

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "success": "登録成功しました。ログインしてください"},
    )

# Webフォーム用ログインルート
@router.post("/login")
def web_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    ok, user = UserService.authenticate(db, username, password)
    if not ok:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "認証失敗"}
        )

    # Cookieにアクセストークンを保存
    access_token = UserService.create_access_token({"username": user.username})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response

# Web API用の認証ルート
@router.post("/api/auth")
def api_login(data: AuthRequest, db: Session = Depends(get_db)):
    ok, user = UserService.authenticate(db, data.username, data.password)
    if not ok:
        raise HTTPException(status_code=401, detail="認証失敗")

    user_permissions = {
        "can_arithmetic": user.can_arithmetic,
        "can_trigonometry": user.can_trigonometry,
        "can_logarithm": user.can_logarithm,
        "is_admin": user.is_admin,
    }

    access_token = UserService.create_access_token({"username": user.username, **user_permissions})
    refresh_token = UserService.create_access_token(
        {"username": user.username, **user_permissions}, expires_delta=timedelta(days=7)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "permissions": [k for k, v in user_permissions.items() if v],
    }


@router.get("/dashboard")
def dashboard(request: Request, access_token: str = Cookie(None)):
    if not access_token:
        return RedirectResponse(url="/?error=アクセストークンが見つかりません")

    ok, payload, user = UserService.verify_access_token(access_token)
    if not ok:
        return RedirectResponse(url="/?error=認証失敗しました")

    granted = user.granted_permissions()

    response = templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "username": payload["username"],
            "permissions": granted,
        }
    )
    # キャッシュ無効化
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response