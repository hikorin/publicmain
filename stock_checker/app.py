import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from logic.stock_data import StockData
from logic.scorer import Scorer

st.set_page_config(page_title="StockOps-YF v2.1", layout="wide")

# --- Styles ---
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #4CAF50;
    }
    .metric-label {
        font-size: 14px;
        color: #AAA;
    }
    .score-circle {
        font-size: 40px;
        font-weight: bold;
        color: #2196F3;
    }
    
    /* Mobile-friendly adjustments */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 20px;
        }
        .metric-label {
            font-size: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Functions ---

def analyze_stock(ticker, context="Scanner"):
    if not ticker:
        return

    if not ticker.endswith(".T"):
        ticker = f"{ticker}.T"

    stock = StockData(ticker)
    
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            stock.fetch_data()
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return

    current_price = stock.get_current_price()
    if current_price is None:
        st.error("No price data found.")
        return

    scorer = Scorer(stock)
    
    col1, col2 = st.columns([1, 2])

    with col1:
        company_name = stock.get_company_name()
        st.subheader(f"{company_name} ({ticker}) 分析")
        st.metric("現在値", f"¥{current_price:,.0f}")

        # Scores
        short_res = scorer.evaluate_short_term()
        med_res = scorer.evaluate_medium_term()

        st.markdown("### スコア評価")
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='metric-card'><div class='metric-value'>{short_res['score']}</div><div class='metric-label'>短期モメンタム</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><div class='metric-value'>{med_res['score']}</div><div class='metric-label'>中期ファンダメンタルズ</div></div>", unsafe_allow_html=True)

    with col2:
        # Chart
        if stock.hist is not None:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=stock.hist.index,
                            open=stock.hist['Open'],
                            high=stock.hist['High'],
                            low=stock.hist['Low'],
                            close=stock.hist['Close'],
                            name='株価'))
            fig.update_layout(title=f"{ticker} 株価チャート", height=400, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    # Details
    st.markdown("---")
    d1, d2 = st.columns(2)
    
    with d1:
        st.markdown("#### 短期戦略シグナル (モメンタム)")
        if short_res['details']:
            for d in short_res['details']:
                st.write(f"- {d}")
        else:
            st.write("特筆すべきシグナルなし")
            
    with d2:
        st.markdown("#### 中期戦略シグナル (ファンダメンタルズ)")
        if med_res['details']:
            for d in med_res['details']:
                st.write(f"- {d}")
        else:
            st.write("特筆すべきシグナルなし")

    return current_price, short_res, med_res

# --- Layout ---

st.title("StockOps-YF v2.1 📈")

# Sidebar: Portfolio
st.sidebar.header("ポートフォリオ監視")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

with st.sidebar.form("add_stock"):
    pf_ticker = st.text_input("銘柄コード (例: 7203)", max_chars=6)
    pf_price = st.number_input("取得単価 (円)", min_value=0.0, step=100.0)
    add_btn = st.form_submit_button("ウォッチリストに追加")

    if add_btn and pf_ticker:
        if not pf_ticker.endswith(".T"):
            pf_ticker += ".T"
        st.session_state.portfolio.append({"ticker": pf_ticker, "entry": pf_price})
        st.success(f"{pf_ticker} を追加しました")

st.sidebar.markdown("---")
st.sidebar.subheader("ウォッチリスト")

for item in st.session_state.portfolio:
    t = item['ticker']
    entry = item['entry']
    st.sidebar.markdown(f"**{t}** (取得: ¥{entry:,.0f})")

if st.sidebar.button("ポートフォリオ一括スキャン"):
    st.markdown("## ポートフォリオ診断結果")
    for item in st.session_state.portfolio:
        st.markdown(f"### {item['ticker']}")
        analyze_stock(item['ticker'], context="Portfolio")

# Main Scanner
st.markdown("## 銘柄スキャナー")
ticker_input = st.text_input("銘柄コード入力 (例: 8035)", "8035")

if st.button("詳細分析を実行"):
    analyze_stock(ticker_input)

# --- AI Picks Section ---
st.markdown("---")
st.markdown("## 🤖 AI 推奨銘柄 (AIリサーチ)")
st.caption("Gemini + Google検索 (Grounding) による自動分析")

with st.expander("AI設定", expanded=True):
    api_key = st.text_input("Google Gemini APIキーを入力", type="password", help="aistudio.google.com で無料キーを取得できます")

if st.button("🚀 AIリサーチ開始"):
    if not api_key:
        st.error("有効なAPIキーを入力してください。")
    else:
        from logic.ai_researcher import AIResearcher
        
        researcher = AIResearcher(api_key)
        
        with st.status("🤖 AIが調査中...", expanded=True) as status:
            st.write("🔍 Google検索を実行し、最新の市場ニュースを収集しています...")
            st.write("🧠 厳格な基準で分析・選定中...")
            
            # analyze_with_gemini now reads prompt.txt
            ai_results = researcher.analyze_with_gemini()
            
            if "error" in ai_results:
                status.update(label="❌ エラーが発生しました", state="error", expanded=True)
                st.error(ai_results["error"])
            else:
                status.update(label="✅ リサーチ完了！", state="complete", expanded=False)
                st.session_state['ai_results'] = ai_results

# Display Results
if 'ai_results' in st.session_state:
    results = st.session_state['ai_results']
    
    # 1. Full Report (Toggle)
    with st.expander("📝 AI分析レポート全文を表示", expanded=False):
        st.markdown(results.get("full_report", ""))

    # 2. Extracted Stocks Analysis with Split View
    items = results.get("items", [])
    full_text = results.get("full_report", "")

    if items:
        st.markdown("---")
        st.markdown(f"### 📊 AI推奨銘柄分析 ({len(items)}件)")
        
        # Tabs for each stock using AI's Name and Strategy
        # Example tab label: "Toyota (短期)"
        tab_labels = []
        for item in items:
            label = f"{item['name']} ({item['strategy']})"
            tab_labels.append(label)

        tabs = st.tabs(tab_labels)
        
        for i, tab in enumerate(tabs):
            with tab:
                item = items[i]
                ticker = item['ticker']
                strategy = item['strategy']
                
                # Header info
                st.caption(f"推奨区分: **{strategy}** | コード: **{ticker}**")

                # 1. Show yfinance analysis FIRST (Top)
                st.markdown("#### 📈 市場データ分析 (yfinance)")
                # analyze_stock creates columns internally, so we use full width here
                analyze_stock(ticker, context="AI_Pick")

                st.markdown("---")

                # 2. Show AI Perspective BELOW (Bottom)
                st.markdown("#### 🤖 AIの視点 (Gemini)")
                
                # Show specific chunk or full text context
                # Since we have "full_text" in item from parser, we might use that if available?
                # Actually parser says "full_text" is "### ■ ... chunk".
                # Let's use that for precise display.
                if 'full_text' in item and item['full_text']:
                     st.info(item['full_text'])
                else:
                    # Fallback to naive search if parser didn't attach text cleanly
                    if ticker in full_text:
                        start_idx = full_text.find(ticker)
                        snippet = full_text[start_idx:start_idx+1000]
                        st.info(f"...{snippet}...")

    else:
        st.warning("レポートから銘柄コードを抽出できませんでした。「### ■ 銘柄：...（1234）」の形式が含まれているか確認してください。")



