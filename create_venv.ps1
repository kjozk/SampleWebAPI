# UTF-8 にする
chcp 65001

$venvName = "venv"

if (Test-Path $venvName) {
    Write-Host "仮想環境 $venvName は既に存在します。"
} else {
    python -m venv $venvName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "仮想環境作成に失敗しました。Pythonのパスやバージョンを確認してください。"
        exit 1
    }
    Write-Host "仮想環境 $venvName を作成しました。"
}

Write-Host "※仮想環境の有効化はスクリプト実行後に手動で行ってください:"
Write-Host "    .\$venvName\Scripts\Activate.ps1"

Write-Host "pipを最新にアップグレードします..."
& "$venvName\Scripts\python.exe" -m pip install --upgrade pip

Write-Host "必要パッケージをインストールします..."
& "$venvName\Scripts\python.exe" -m pip install fastapi[all] uvicorn[standard] sqlalchemy alembic python-jose passlib
& "$venvName\Scripts\python.exe" -m pip install fastapi-users[sqlalchemy]
& "$venvName\Scripts\python.exe" -m pip install bcrypt==4.0.0

Write-Host "準備完了です。"
