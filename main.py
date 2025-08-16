from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes.user_routes import router as user_router
from routes.feature_routes import router as feature_router
from database import Base, engine
import models.user 

app = FastAPI()

# テーブル作成（起動時に DB にテーブルがなければ作る）
Base.metadata.create_all(bind=engine)

# テンプレートディレクトリの設定
templates = Jinja2Templates(directory="templates")

# ルーターを登録
app.include_router(user_router)
app.include_router(feature_router)

# 静的ファイルが必要なら
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":

    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
