import os
import markdown
from flask import Blueprint
from flask import session, request
from flask import render_template, redirect, url_for, flash, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from services.user_service import UserService
from models import User

user_bp = Blueprint("user", __name__)

DOCS_PATH = os.path.join(os.path.dirname(__file__), "docs")

def make_response(success, message, data=None):
    return jsonify({"status": "success" if success else "error", "message": message, "data": data})

@user_bp.route("/")
def index():
    return render_template("index.html")

# ログイン後のユーザー情報ページ
@user_bp.route("/me")
@jwt_required()
def profile():
    if "username" not in session:
        return redirect(url_for("user.login_page"))

    username = session["username"]
    # DBからユーザー情報を取得
    user = User.query.filter_by(username=username).first()
    return render_template("profile.html", user=user)

# user_bp の中に追加
@user_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

# ログイン
@user_bp.route("/auth/login", methods=["POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    # Content-Type に応じてデータの取得方法を変える
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

    ok, user = UserService.authenticate(username, password)
    if not ok:
        flash("認証失敗", "error")
        return render_template("login.html", username=username), 401

    user_permissions = {
        "can_arithmetic": user.can_arithmetic,
        "can_trigonometry": user.can_trigonometry,
        "can_logarithm": user.can_logarithm,
    }
    granted_permissions = [key for key, val in user_permissions.items() if val]
    additional_claims = user_permissions
    access_token = create_access_token(identity=user.username, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.username)

    session["username"] = user.username

    # Webフォームの場合はユーザー情報ページへリダイレクト
    if not request.is_json:
        flash("ログイン成功", "success")
        return redirect(url_for("user.profile"))

    # APIの場合はJSONで返す
    return jsonify({
        "status": "success",
        "message": "認証成功",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "permissions": granted_permissions,
        }
    })

# 登録
@user_bp.route("/users", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if password != password2:
            flash("パスワードが一致しません", "error")
            return render_template("register.html", username=username)

        ok, msg = UserService.create_user(username, password)
        if ok:
            flash("登録成功しました。ログインしてください", "success")
            return redirect(url_for("user.login"))  # ログインページにリダイレクト
        else:
            flash(msg, "error")
            return render_template("register.html", username=username)

    # GETはフォーム表示
    return render_template("register.html")

# パスワード変更
@user_bp.route("/users/me/password", methods=["PATCH"])
@jwt_required()
def change_password():
    data = request.get_json()
    username = get_jwt_identity()
    ok, msg = UserService.change_password(username, data["old_password"], data["new_password"])
    status = 200 if ok else 400
    return make_response(ok, msg), status

# 削除
@user_bp.route("/users/<string:target_username>", methods=["DELETE"])
@jwt_required()
def delete_user(target_username):
    claims = get_jwt()
    current_user = get_jwt_identity()
    if not claims.get("is_admin") and current_user != target_username:
        return make_response(False, "権限がありません"), 403
    ok, msg = UserService.delete_user(target_username)
    status = 200 if ok else 404
    return make_response(ok, msg), status

@user_bp.route("/dashboard")
@jwt_required()
def dashboard():
    claims = get_jwt()  # JWTのカスタムクレームから権限取得

    # 権限を持っているドキュメントを読み込む
    docs_html = []
    if claims.get("can_arithmetic"):
        docs_html.append(load_markdown("arithmetic.md"))
    if claims.get("can_trigonometry"):
        docs_html.append(load_markdown("trigonometry.md"))
    if claims.get("can_logarithm"):
        docs_html.append(load_markdown("logarithm.md"))

    return render_template("dashboard.html", docs_html=docs_html)

def load_markdown(filename):
    filepath = os.path.join(DOCS_PATH, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        md_content = f.read()
    return markdown.markdown(md_content, extensions=["fenced_code", "tables"])

