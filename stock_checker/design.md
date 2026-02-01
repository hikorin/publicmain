# Webアプリ設計仕様書：StockOps-YF v2.1 (財務・相関統合モデル)

## 1. システム概要
本システムは、`yfinance` ライブラリをデータソースとし、日本株（東証上場銘柄）を対象に「短期的な需給（モメンタム）」と「中期的な企業価値（ファンダメンタルズ）」を二軸で評価・監視するWebアプリケーションである。
**特徴**: Streamlitをベースにしつつ、Custom CSSによる「Glassmorphism（すりガラス）」デザインを採用し、高い視認性とモダンなUXを提供する。

---

## 2. 投資戦略の定義とロジック

### 2.1 短期・モメンタム戦略 (Short-term Strategy)
市場全体（日経平均）に対する感応度と、直近の過熱感からエントリー/エグジットを判定する。

* **市場感度（$\beta$値）:** 
    * 日経平均（`^N225`）と個別銘柄の過去20日間の日次収益率を用いた回帰分析。
    * $\beta > 1.2$ を「強気トレンド追随」の条件とする。
* **テクニカル指標:**
    * **RSI (14日):** 30以下（売られすぎ・反発狙い）、80以上（買われすぎ・利確）。
    * **出来高:** 直近5日平均の1.5倍以上の急増を「資金流入」のシグナルとする。

### 2.2 中期・バリューアップ戦略 (Medium-term Strategy)
企業の「稼ぐ力」と「財務健全性」を評価し、適正株価との乖離を狙う。

| 評価カテゴリ | 指標 (yfinance Key) | 判定しきい値 |
| :--- | :--- | :--- |
| **収益性** | `returnOnEquity` (ROE) | 10% 以上 |
| **割安性** | `trailingPE` (PER) | 15倍 以下 |
| **安全性** | `totalStockholderEquity / totalAssets` | 40% 以上 |
| **成長性** | `revenueGrowth` | 前年比 +5% 以上 |

### 2.3 UI/UXデザイン
* **コンセプト**: "Rich & Cool" - 従来の分析ツールの無機質さを排除し、近未来的な金融ダッシュボードを表現。
* **スタイル**:
    * **Glassmorphism**: 半透明なカードとぼかし効果（Backend Blur）により、情報の階層を視覚的に整理。
    * **Typography**: Google Fonts "Outfit" を採用し、可読性とデザイン性を両立。
    * **Theme**: 深みのあるダークテーマと、視認性の高いネオンアクセントカラー。

---

## 3. アプリケーション機能仕様

### F-1: 銘柄スキャナー (Scanner)
* 銘柄コードを入力すると、`yfinance` からリアルタイム価格と財務諸表を取得。
* 「短期スコア」と「中期スコア」をそれぞれ100点満点で算出し、判定結果を出力。

### F-2: ポートフォリオ・モニター (Watchlist)
* 保有銘柄の「取得単価」を登録し、現在の損益（％）を表示。
* **アラート機能**: 損切りライン（短期 $-3\%$ / 中期 $-10\%$）到達時に強調表示。財務変化も検知。

### F-3: AIリサーチ (AI Research)
* **概要**: Gemini (Generative AI) と Google検索 (Grounding) を活用し、Web上の最新ニュースや市況から有望銘柄を自動発掘する。
* **処理フロー**:
    1. **認証**: 環境変数 `GEMINI_API_KEY` または画面入力によりAPIキーを認証。
    2. **モデル選択**: 使用するGeminiモデル（例: `gemini-3-pro-preview`, `gemini-2.5-flash`, `gemini-1.5-pro` 等）を画面上で選択可能。
    3. **プロンプト読み込み**: `prompt.txt` から分析指示を読み込む（クラウド環境でのパス解決に対応）。
    4. **AI分析 (Grounding)**: GeminiがGoogle検索を実行し、最新市場動向に基づき銘柄を選定。
    5. **解析 (Parsing)**: レポートから銘柄コードを抽出。
    6. **統合評価**: 抽出銘柄に対して `yfinance` によるリアルタイム分析を実行し、AIの定性評価と市場データの定量評価を並列表示。

---

## 4. データ構造 (Data Schema)

```json
{
  "stock_code": "8035.T",
  "strategy": "Medium",
  "entry_price": 42000,
  "metrics": {
    "current_beta": 1.45,
    "rsi": 45.2,
    "roe": 0.18,
    "debt_ratio": 0.35
  }
}
```

---

## 5. 環境構築・デプロイ (Setup & Deployment)

### 5.1 ローカル実行
前提: Python 3.10以上推奨

1. **インストール**
   ```bash
   pip install -r requirements.txt
   ```
2. **起動**
   ```bash
   streamlit run app.py
   ```

### 5.2 環境変数 (Environment Variables)
セキュリティ向上のため、APIキーは環境変数での管理を推奨します。Render等のPaaSデプロイ時もこの方法を使用します。

| 変数名 | 説明 |
| :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini APIキー (AIza...) |

### 5.3 クラウドデプロイ (Render)
本システムは Render.com での動作に対応しています。
* **Runtime**: Python 3
* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `streamlit run app.py`
* **Environment**: `GEMINI_API_KEY` を設定してください。