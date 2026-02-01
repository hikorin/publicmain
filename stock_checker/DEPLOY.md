# Render デプロイガイド

このアプリケーションは、Render (render.com) で実行できるように設計されています。

## 1. Web Service の新規作成
- 自身の GitHub リポジトリを接続します。
- `stock_checker` リポジトリを選択します。

## 2. 設定の詳細
- **Name**: `stock-checker-app` (または任意の名)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py`

## 3. 環境変数の設定 (重要)
APIキーを毎回入力しなくて済むよう、環境変数を設定してください。

| キー | 値 |
| --- | --- |
| `GEMINI_API_KEY` | 自身の Google Gemini APIキー (`AIza...` で始まる文字列) |

## 4. デプロイの実行
- 「Create Web Service」をクリックします。
- ビルドが完了すると、アプリケーションが全世界に公開されます。

## 補足事項
- `requirements.txt` に `google-genai` と `streamlit` が含まれていることが必須です。
- クラウド環境（Render等）での `prompt.txt` の読み込みエラーについては、`ai_researcher.py` 内でパスの解決を修正済みです。

## ローカル開発での環境変数設定
ローカルで開発する際は、`.env` ファイルを使用できます：

1. `.env.example` をコピーして `.env` を作成
   ```bash
   cp .env.example .env
   ```

2. `.env` ファイルにAPIキーを記載
   ```
   GEMINI_API_KEY=AIza...your_actual_key
   ```

3. アプリを起動（`.env` が自動的に読み込まれます）
   ```bash
   streamlit run app.py
   ```

**注意**: `.env` ファイルは `.gitignore` に含まれているため、Gitにアップロードされません。
