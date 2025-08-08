from flask_jwt_extended import jwt_required, get_jwt
from flask import Blueprint, jsonify, request
import math

feature_bp = Blueprint("feature", __name__)

@feature_bp.route("/add", methods=["POST"])
@jwt_required()
def add_numbers():
    claims = get_jwt()
    if not claims.get("can_addition", False):
        return jsonify({"status": "error", "message": "四則演算の権限がありません"}), 403

    data = request.get_json()
    try:
        a = float(data.get("a"))
        b = float(data.get("b"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "数値 'a' と 'b' を正しく指定してください"}), 400

    result = a + b
    return jsonify({"status": "success", "result": result})

@feature_bp.route("/sin", methods=["POST"])
@jwt_required()
def calculate_sin():
    claims = get_jwt()
    if not claims.get("can_trigonometry", False):
        return jsonify({"status": "error", "message": "三角関数の権限がありません"}), 403

    data = request.get_json()
    try:
        x = float(data.get("x"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "数値 'x' を正しく指定してください"}), 400

    result = math.sin(x)
    return jsonify({"status": "success", "result": result})
