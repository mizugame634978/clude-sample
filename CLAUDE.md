# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Django ベースのログイン機能付きTodoアプリケーション。MVT（Model-View-Template）パターンに従い、開発環境ではSQLiteデータベースを使用。

## 基本コマンド

### 開発サーバー起動
```bash
uv run python manage.py runserver
```

### データベース操作
```bash
# マイグレーション適用
uv run python manage.py migrate

# モデル変更後の新しいマイグレーション作成
uv run python manage.py makemigrations
```

### テスト実行
```bash
# 全テスト実行
uv run python manage.py test

# 特定のテストクラス実行
uv run python manage.py test todo.tests.AuthenticationTestCase
uv run python manage.py test todo.tests.TodoCRUDTestCase

# テストカバレッジ
uv add coverage
uv run coverage run --source='.' manage.py test
uv run coverage report
```

### パッケージ管理
```bash
# 依存関係インストール
uv sync

# 新しいパッケージ追加
uv add package_name
```

## アーキテクチャ

### 主要コンポーネント
- **Models**: `todo/models.py` - ユーザー関連付きTodoモデル
- **Views**: `todo/views.py` - 認証とCRUD操作
- **Forms**: `todo/forms.py` - Todo作成・編集用フォーム
- **Templates**: Bootstrap 5.1.3を使用したサーバーサイドレンダリング

### 認証システム
- カスタム登録ビュー（`todo/views.py:register_view`）
- `request.user`によるユーザー別Todo絞り込み
- ログイン・ログアウトはDjangoの組み込みビューを使用

### データベーススキーマ
- Todoモデルフィールド: title, description, completed, created_at, user（外部キー）
- ユーザーモデル: Djangoの組み込みUserモデル

### フロントエンド
- Bootstrap 5.1.3 + jQuery 3.6.0
- ベーステンプレート: `templates/base.html`
- AJAX機能付きレスポンシブデザイン

## 開発時の注意点

### 言語・地域設定
- `LANGUAGE_CODE = 'ja'`（日本語）
- `TIME_ZONE = 'Asia/Tokyo'`

### セキュリティ機能
- CSRF保護有効
- Todo操作にはユーザー認証が必要
- ユーザーは自分のTodoのみアクセス可能

### テスト構成
- `todo/tests.py`に2つのメインテストクラス
- 認証テストとCRUD操作テスト
- ユーザーフローの包括的なカバレッジ

### コード作成
- ドキュメントとUIは日本語
- ソースコードのコメントも日本語
- Docstringはgoogleスタイルで、引数と戻り値は型ヒントを使用

### Gitコミット規約
コミットメッセージは以下の形式に従う：

```
<type>: <description>

<body>
```

**コミットタイプ：**
- `feat:` - 新機能の追加
- `fix:` - バグ修正
- `docs:` - ドキュメントの変更
- `style:` - コードフォーマットの変更（機能に影響しない）
- `refactor:` - リファクタリング
- `test:` - テストの追加・修正
- `chore:` - ビルドプロセスやツールの変更

**コミット内容は日本語で記載：**
```bash
# 例
git commit -m "feat: ユーザー認証機能を追加"
git commit -m "fix: Todo削除時のバリデーションエラーを修正"
git commit -m "docs: READMEにインストール手順を追加"
```