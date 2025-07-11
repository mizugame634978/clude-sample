# Django Todo App

Djangoで作成されたログイン機能付きTodoアプリケーションです。ユーザー認証機能とTodoのCRUD操作を提供します。

## プロジェクト概要

このプロジェクトは、個人のタスク管理を目的としたWebアプリケーションです。各ユーザーは自分専用のTodoリストを作成・管理できます。

### 主な機能

- **ユーザー認証**
  - ユーザー登録
  - ログイン・ログアウト
  - セッション管理

- **Todo管理**
  - Todo作成
  - Todo一覧表示
  - Todo編集
  - Todo削除
  - 完了状態の切り替え
  - ユーザー別のTodo管理

## 使用技術

- **バックエンド**
  - Python 3.10+
  - Django 5.2.3
  - PostgreSQL 15 (Docker環境)
  - SQLite (ローカル開発・テスト環境)

- **フロントエンド**
  - HTML5
  - Bootstrap 5.1.3
  - jQuery 3.6.0

- **パッケージ管理**
  - uv (Python パッケージマネージャー)

- **インフラ**
  - Docker & Docker Compose
  - PostgreSQL 15

- **テスト**
  - Django Test Framework

## 初期設定

### Docker環境（推奨）

#### 前提条件
- Docker
- Docker Compose

#### セットアップ手順

```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd todoapp

# 2. Docker環境の起動
docker-compose up -d

# 3. データベースの初期化
docker-compose exec web uv run python manage.py migrate

# 4. 管理者ユーザーの作成（オプション）
docker-compose exec web uv run python manage.py createsuperuser
```

### ローカル環境

#### 前提条件
- Python 3.10+
- uv

#### セットアップ手順

```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd todoapp

# 2. uvのインストール
curl -LsSf https://astral.sh/uv/install.sh  < /dev/null |  sh
source $HOME/.local/bin/env

# 3. 依存関係のインストール
uv sync

# 4. データベースの初期化
uv run python manage.py migrate

# 5. 管理者ユーザーの作成（オプション）
uv run python manage.py createsuperuser
```

## プロジェクトの起動方法

### 方法1: Docker Compose（推奨）

PostgreSQLを使用した本番に近い環境でアプリケーションを実行：

```bash
# Docker Composeでアプリケーションを起動
docker-compose up -d

# データベースの初期化（初回のみ）
docker-compose exec web uv run python manage.py migrate

# 管理者ユーザーの作成（オプション）
docker-compose exec web uv run python manage.py createsuperuser
```

サーバーが起動したら、ブラウザで `http://127.0.0.1:8000/` にアクセスしてください。

### 方法2: ローカル環境（開発用）

```bash
source $HOME/.local/bin/env
uv run python manage.py runserver
```

サーバーが起動したら、ブラウザで `http://127.0.0.1:8000/` にアクセスしてください。

### 初回アクセス時の手順

1. `http://127.0.0.1:8000/register/` にアクセスして新規ユーザーを作成
2. 作成したアカウントでログイン
3. Todoの作成・管理を開始

## テストの実行方法

### Docker環境でのテスト実行

```bash
# SQLiteを使用してテスト実行（高速）
docker-compose exec web env USE_SQLITE_FOR_TESTS=true uv run python manage.py test

# PostgreSQLを使用してテスト実行
docker-compose exec web uv run python manage.py test
```

### ローカル環境でのテスト実行

```bash
# SQLiteを使用してテスト実行（推奨）
USE_SQLITE_FOR_TESTS=true uv run python manage.py test

# PostgreSQL環境でのテスト実行（DBが起動している場合）
uv run python manage.py test
```

### 特定のテストクラスの実行

```bash
# 認証関連のテストのみ実行
uv run python manage.py test todo.tests.AuthenticationTestCase

# CRUD関連のテストのみ実行
uv run python manage.py test todo.tests.TodoCRUDTestCase
```

### テストカバレッジの確認

```bash
uv add coverage
uv run coverage run --source='.' manage.py test
uv run coverage report
uv run coverage html  # HTMLレポートの生成
```

## ディレクトリ構成

```
todoapp/
├── README.md                 # このファイル
├── main.py                   # uvプロジェクトのメインファイル
├── pyproject.toml           # プロジェクト設定と依存関係
├── uv.lock                  # 依存関係のロックファイル
├── manage.py                # Django管理コマンド
├── db.sqlite3              # SQLiteデータベース（実行後に生成）
├── todoproject/            # Djangoプロジェクト設定
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Django設定
│   ├── urls.py             # プロジェクトのURL設定
│   └── wsgi.py
├── todo/                   # Todoアプリケーション
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py            # フォーム定義
│   ├── models.py           # データモデル
│   ├── tests.py            # テストコード
│   ├── urls.py             # アプリのURL設定
│   ├── views.py            # ビュー関数
│   └── migrations/         # データベースマイグレーション
│       └── 0001_initial.py
└── templates/              # HTMLテンプレート
    ├── base.html           # ベーステンプレート
    ├── registration/       # 認証関連テンプレート
    │   ├── login.html
    │   └── register.html
    └── todo/               # Todo関連テンプレート
        ├── todo_list.html
        ├── todo_form.html
        └── todo_confirm_delete.html
```

## 主要ファイルの説明

### バックエンド

- **`todo/models.py`**: Todoモデルの定義（タイトル、詳細、完了状態、ユーザー関連付け）
- **`todo/views.py`**: ビュー関数（認証、CRUD操作）
- **`todo/forms.py`**: フォームクラス（Todo作成・編集用）
- **`todo/tests.py`**: テストコード（認証とCRUD操作のテスト）

### フロントエンド

- **`templates/base.html`**: 共通レイアウト
- **`templates/todo/todo_list.html`**: Todo一覧画面
- **`templates/registration/login.html`**: ログイン画面

### 設定

- **`todoproject/settings.py`**: Django設定（データベース、認証、国際化）
- **`pyproject.toml`**: uvプロジェクト設定と依存関係

## 開発時の注意事項

- データベースの変更を行った場合は、必ずマイグレーションを実行してください
- 新しい機能を追加した場合は、対応するテストコードも作成してください
- 本番環境では、`DEBUG = False` に設定し、適切なデータベースを使用してください

## Claude Code設定

`.claude-code-settings.json`はチーム開発用のClaude Code自動実行設定です。`mkdir -p ~/.config/claude-code && cp .claude-code-settings.json ~/.config/claude-code/settings.json`で個人環境に設定してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
