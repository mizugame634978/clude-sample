#!/bin/bash

# プロジェクトのルートにあるGEMINI.mdのパスを取得
GEMINI_MD_PATH="$(pwd)/GEMINI.md"

if [ -f "$GEMINI_MD_PATH" ]; then
  echo "プロジェクトのルールを読み込みます。以下の内容をコピーして、Geminiに貼り付けてください。"
  echo "---"
  # 指示文とファイル読み込みコマンドを組み合わせる
  echo "このプロジェクトのルールを読み込んで、以降のやり取りで厳守してください。 read_file $GEMINI_MD_PATH"
  echo "---"
else
  echo "GEMINI.mdが見つかりません。"
fi

# ここでGemini CLIを起動するコマンドを続ける（もしあれば）
