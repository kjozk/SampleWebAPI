from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

feature_bp = Blueprint("feature", __name__)

@feature_bp.route("/add", methods=["POST"])
@jwt_required()
def add_numbers():
    data = request.get_json()
    try:
        a = float(data.get("a"))
        b = float(data.get("b"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "数値 'a' と 'b' を正しく指定してください"}), 400

    result = a + b
    return jsonify({"status": "success", "result": result})
