from flask import Flask
from extensions import db, jwt
from routes.user_routes import user_bp
from routes.feature_routes import feature_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 拡張の初期化
db.init_app(app)
jwt.init_app(app)

# ルート登録
app.register_blueprint(user_bp)
app.register_blueprint(feature_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
