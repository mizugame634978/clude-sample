# Python 3.10を使用（要件通りPythonバージョン固定）
FROM python:3.10-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新とPostgreSQL開発用ライブラリをインストール
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# uvをインストール
RUN pip install uv

# プロジェクトファイルをコピー
COPY pyproject.toml uv.lock ./

# uvで依存関係をインストール
RUN uv sync --frozen

# アプリケーションコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# 開発サーバーを起動
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]