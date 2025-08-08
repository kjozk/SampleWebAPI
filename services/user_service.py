from models import User
from extensions import db

class UserService:
    @staticmethod
    def create_user(username, password):
        if User.query.filter_by(username=username).first():
            return False, "ユーザー名は既に存在します"
        user = User(username=username)
        user.can_addition = True
        user.can_trigonometry = False
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return True, "登録成功"

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return True, user
        return False, None

    @staticmethod
    def change_password(username, old_pw, new_pw):
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(old_pw):
            return False, "旧パスワードが違います"
        user.set_password(new_pw)
        db.session.commit()
        return True, "パスワード変更成功"

    @staticmethod
    def delete_user(username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return False, "ユーザーが存在しません"
        db.session.delete(user)
        db.session.commit()
        return True, f"ユーザー {username} を削除しました"
