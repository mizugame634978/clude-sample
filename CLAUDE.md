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
### 開発手法
- TDD(テスト駆動開発)を開発手法とする
- 先にテストコードを書いてから実装を始め、開発した機能がテストを追加して初めてPRを提出できる
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

#### 通常のコミット
```
<type>: <description>

<body>
```

#### Issue対応のコミット
```
#<issue番号> <type>: <description>

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
# 通常のコミット例
git commit -m "feat: ユーザー認証機能を追加"
git commit -m "fix: Todo削除時のバリデーションエラーを修正"

# Issue対応のコミット例
git commit -m "#1 feat: Todo優先度機能を追加"
git commit -m "#2 fix: ログイン時のCSRFエラーを修正"
```

## 新人エンジニア作業フロー

### Issue駆動開発のワークフロー
要件の依頼を受けた際は、以下の手順で作業を進める：

**重要な原則**: 
- 完了したIssueはクローズしてもよいが、削除してはならない
- Issue履歴はプロジェクトの貴重な記録として保持する

#### 1. 問題の分析と課題整理
```bash
# TodoWriteツールで作業タスクを管理
- 問題の調査
- 原因特定
- 解決方針の策定
- テスト計画
```

#### 2. Issue作成
```bash
# GitHub Issueで問題を文書化
gh issue create --title "bug: 具体的なエラー内容" --body "$(cat <<'EOF'
## 問題の概要
具体的な問題の説明

## 再現手順
1. 操作手順を明記
2. エラーの発生条件
3. 期待される動作

## 原因
技術的な原因の分析

## 影響範囲
影響を受ける機能や範囲

## 優先度
High/Medium/Low
EOF
)"
```

#### 3. 作業ブランチ作成と実装
```bash
# Issue対応のブランチ名規則
git checkout -b feature/issue番号

# 実装とテスト
uv run python manage.py test

# コミット（Issue番号付きコミット規約に従う）
git add .
git commit -m "#issue番号 feat: 機能の具体的な実装内容"
```

#### 4. プルリクエスト作成
```bash
# リモートにプッシュ
git push -u origin feature/issue番号

# PR作成（Issue番号を含める）
gh pr create --title "#issue番号 feat: 機能の具体的な実装内容" --body "$(cat <<'EOF'
## 概要
Issueで報告された問題の修正

## 問題
具体的な問題の説明

## 解決方法
実装した解決策の説明

## 変更内容
- 変更したファイルと内容を箇条書き

## テスト結果
- ✅ 既存テスト○件すべて通過
- ✅ 新規テスト○件追加

## 動作確認
修正前: エラー内容
修正後: 正常な動作

## レビューポイント
レビューで確認してほしい点

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

#### 5. レビュー対応
レビューコメントを受けた際は：
```bash
# 追加作業（テスト追加など）
# 同じブランチで追加コミット
git add .
git commit -m "#issue番号 test: レビュー指摘事項への対応内容"
git push

# レビュアーに対応完了を報告
# PRコメントには必ず署名を記載
gh pr comment プル番号 --body "コメント内容

🤖 Generated with [Claude Code](https://claude.ai/code)"
```

#### 6. マージ後のクリーンアップ
```bash
# mainブランチに戻る
git checkout main
git pull

# 作業ブランチを削除
git branch -d feature/issue番号

# 完了したIssueをクローズ（削除は禁止）
gh issue close issue番号 --comment "PRのマージにより対応完了"
```

### ファイル整理の原則

#### 一時的なスクリプトファイルの管理
作業中に作成した一時的なファイルは、適切な場所に整理する：

```bash
# 参考資料として残す場合
mkdir -p docs/pr-history
mv 一時ファイル.sh docs/pr-history/

# 不要な場合は削除
rm 一時ファイル

# 変更をコミット
git add docs/
git commit -m "chore: 一時ファイルを適切な場所に整理"
git push
```

#### フォルダ命名規則
- `.github/` - GitHub設定用（触らない）
- `docs/` - プロジェクト文書・参考資料
- `scripts/` - 運用スクリプト
- `tools/` - 開発ツール

### 品質保証の原則

#### テスト追加の指針
バグ修正時は、同様の問題を検知できるテストを必ず追加：
```python
class 問題名TestCase(TestCase):
    def test_正常系(self):
        # 修正後の正常動作を確認
        
    def test_異常系(self):
        # 問題が再発した場合のエラー検知
```

#### コミット前チェックリスト
- [ ] 全テストが通過している
- [ ] 適切なコミットメッセージ（タイプ:日本語説明）
- [ ] 必要に応じてテストを追加
- [ ] 一時ファイルの整理
- [ ] レビュー観点を明確化
```

### 作業メモリ

- 12のissueを実装し、PRを出して