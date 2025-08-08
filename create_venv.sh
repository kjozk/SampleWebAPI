#!/bin/bash

venv_name="venv"

if [ -d "$venv_name" ]; then
    echo "仮想環境 $venv_name は既に存在します。"
else
    python3 -m venv "$venv_name"
    echo "仮想環境 $venv_name を作成しました。"
fi

echo "仮想環境を有効化します..."
source "$venv_name/bin/activate"
echo "有効化されました。"

echo "必要パッケージをインストールします..."
pip install --upgrade pip
pip install flask flask_sqlalchemy flask_jwt_extended werkzeug

echo "準備完了です。"
