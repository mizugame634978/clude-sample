#!/bin/bash

# Issue作成
echo "Creating Issue..."
gh issue create --title "bug: Todo完了ボタンでCSRF 403エラーが発生" --body "## 問題の概要
Todo一覧画面で完了ボタン（チェックボックス）をクリックすると、以下のエラーが発生します：

\`\`\`
[24/Jun/2025 21:57:19] \"POST /toggle/2/ HTTP/1.1\" 403 2534
\`\`\`

## 再現手順
1. 開発サーバーを起動: \`uv run python manage.py runserver\`
2. Todo一覧画面にアクセス
3. 任意のTodoの完了チェックボタンをクリック
4. HTTP 403エラーが発生

## 原因
- AJAX POST リクエストにCSRFトークンが含まれていない
- \`todo_list.html\`でJavaScriptが\`\$('[name=csrfmiddlewaretoken]').val()\`でCSRFトークンを取得しようとしているが、テンプレートに\`{% csrf_token %}\`タグが存在しない

## 期待される動作
完了ボタンをクリックした際に、正常にTodoの完了状態が切り替わること

## 影響範囲
- Todo完了状態の切り替え機能が使用不可
- ユーザビリティの低下

## 優先度
High - 主要機能の一つが動作しない" --label "bug,csrf,javascript,high-priority"

echo ""
echo "Creating Pull Request..."
gh pr create --title "fix: Todo完了ボタンのCSRF 403エラーを修正" --body "## 概要
Issue で報告されたTodo完了ボタンクリック時のCSRF 403エラーを修正しました。

## 問題
- \`todo_list.html\`のJavaScriptでCSRFトークンを取得しようとしているが、テンプレートに\`{% csrf_token %}\`タグが存在しない
- そのため、AJAX POSTリクエスト時にCSRFトークンが\`undefined\`となり403エラーが発生

## 解決方法
- \`templates/todo/todo_list.html\`に\`{% csrf_token %}\`タグを追加
- 既存のJavaScriptコードがCSRFトークンを正常に取得できるようになる

## 変更内容
- \`templates/todo/todo_list.html\`の\`{% block content %}\`直下に\`{% csrf_token %}\`を追加

## テスト結果
- ✅ 既存テスト21件すべて通過
- ✅ 回帰テストでの問題なし

## 動作確認
修正前:
\`\`\`
[24/Jun/2025 21:57:19] \"POST /toggle/2/ HTTP/1.1\" 403 2534
\`\`\`

修正後:
- Todo完了ボタンクリック時に正常に状態が切り替わる
- 403エラーが発生しない

## レビューポイント
- CSRFトークンが適切にテンプレートに埋め込まれているか
- 既存機能に影響がないか
- セキュリティ要件を満たしているか

🤖 Generated with [Claude Code](https://claude.ai/code)"

echo ""
echo "Issue and PR creation completed!"