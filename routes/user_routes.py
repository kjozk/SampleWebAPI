from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from services.user_service import UserService
from models import User

user_bp = Blueprint("user", __name__)

def make_response(success, message, data=None):
    return jsonify({"status": "success" if success else "error", "message": message, "data": data})

# ログイン
@user_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    ok, user = UserService.authenticate(data["username"], data["password"])
    if not ok:
        return make_response(False, "認証失敗"), 401

    user_permissions = {
        "can_addition": user.can_addition,
        "can_trigonometry": user.can_trigonometry,
        "can_logarithm": user.can_logarithm,
    }
    granted_permissions = [key for key, val in user_permissions.items() if val]
    additional_claims = user_permissions
    access_token = create_access_token(identity=user.username, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.username)

    return make_response(True, "認証成功", {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "permissions": granted_permissions,
    })

# 登録
@user_bp.route("/users", methods=["POST"])
def register():
    data = request.get_json()
    if data["password"] != data["password2"]:
        return make_response(False, "パスワードが一致しません"), 400
    ok, msg = UserService.create_user(data["username"], data["password"])
    status = 200 if ok else 400
    return make_response(ok, msg), status

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
