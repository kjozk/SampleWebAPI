# UTF-8にするために chcp 65001 を先頭で実行することを推奨
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

Write-Host "仮想環境を有効化します..."
& "$venvName\Scripts\Activate.ps1"
Write-Host "有効化されました。"

Write-Host "pipを最新にアップグレードします..."
pip install --upgrade pip

Write-Host "必要パッケージをインストールします..."
pip install flask flask_sqlalchemy flask_jwt_extended werkzeug

Write-Host "準備完了です。"
