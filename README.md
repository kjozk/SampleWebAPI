# SampleWebAPI

## 概要

本プロジェクトは、Flaskを使ったユーザー認証・管理APIのサンプル実装です。
JWTによる認証と権限管理を備えています。
主な機能は以下の通りです。

- ユーザー登録
- ユーザー認証（JWT発行）
- パスワード変更
- ユーザー削除（管理者権限または本人のみ）
- 認証必須の機能API
  - 足し算

## 環境構築

### 1. Python 3.8以上をインストールしてください

### 2. 仮想環境作成（Windows PowerShell例）

```shell
.\create_venv.ps1
```

### 3. 仮想環境有効化


Windows PowerShell:

```shell
.\venv\Scripts\Activate.ps1
```

Linux/macOS (bash):

```bash
source venv/bin/activate
```

## 実行

```bash
python app.py
```

## API実行サンプル（curl）

### 1. ユーザー登録

Windows PowerShell:

```shell
Invoke-WebRequest -Uri http://localhost:5000/users `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"username":"testuser", "password":"pass1234", "password2":"pass1234"}'
```

Linux/macOS (bash):

```bash
curl -X POST http://localhost:5000/users -H "Content-Type: application/json" -d "{\"username\":\"testuser\", \"password\":\"pass1234\", \"password2\":\"pass1234\"}"
```

### 2. ログイン（認証）

Windows PowerShell:

```shell
$response = Invoke-WebRequest -Uri http://localhost:5000/auth/login `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{ "username": "testuser", "password": "pass1234" }'
$data = $response.Content | ConvertFrom-Json
$accessToken = $data.data.access_token
```

Linux/macOS (bash):

```bash
curl -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"testuser\", \"password\":\"pass1234\"}"
```

成功するとJSONで `access_token` と `refresh_token` が返ってきます。

### 3. パスワード変更（トークン必須）

```bash
curl -X PATCH http://localhost:5000/users/me/password -H "Content-Type: application/json" -H "Authorization: Bearer <アクセストークン>" -d "{\"old_password\":\"pass1234\", \"new_password\":\"newpass5678\"}"
```

### 4. ユーザー削除（管理者または本人）

```bash
curl -X DELETE http://localhost:5000/users/testuser -H "Authorization: Bearer <アクセストークン>"
```

### 認証必須の機能API

#### 足し算

Windows PowerShell:

```shell
Invoke-WebRequest -Uri http://localhost:5000/add `
  -Method POST `
  -Headers @{ 
      "Content-Type" = "application/json"; 
      "Authorization" = "Bearer $accessToken" 
  } `
  -Body '{ "a": 10, "b": 20 }'
```

Python:

```python
import requests

BASE_URL = "http://localhost:5000"

def login_user(username, password):
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": username,
        "password": password
    }
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        data = r.json()
        access_token = data["data"]["access_token"]
        print("Login successful. Access token:", access_token)
        return access_token
    else:
        print(f"Login failed: {r.status_code} {r.text}")
        return None

def add_numbers(token, a, b):
    url = f"{BASE_URL}/add"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"a": a, "b": b}
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 200:
        print("Addition result:", r.json()["result"])
    else:
        print(f"Addition API error: {r.status_code} {r.text}")

if __name__ == "__main__":
    username = "testuser"
    password = "pass1234"

    token = login_user(username, password)

    if token:
        add_numbers(token, 10, 20)
```
