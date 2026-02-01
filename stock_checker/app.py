import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
from logic.stock_data import StockData
from logic.scorer import Scorer

# Load environment variables from .env file (for local development)
# In production (e.g., Render), OS-level env vars take precedence
load_dotenv()

st.set_page_config(page_title="StockOps-YF v2.1", layout="wide")

# --- Styles ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Dark Theme Background */
    .stApp {
        background-color: #0a0e1a;
        background-image: radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.08) 0%, transparent 50%),
                          radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
        color: #e5e7eb;
    }

    /* Glassmorphism Card - Higher Contrast */
    .metric-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        margin-bottom: 16px;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px -4px rgba(59, 130, 246, 0.3);
        border-color: rgba(59, 130, 246, 0.4);
    }

    /* Typography - Solid Colors for Readability */
    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        color: #22d3ee;
        margin-bottom: 6px;
        text-shadow: 0 0 20px rgba(34, 211, 238, 0.3);
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #cbd5e1;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Buttons - High Contrast */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: #ffffff !important;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.5);
        background: linear-gradient(135deg, #60a5fa, #3b82f6);
    }

    /* Inputs - Better Visibility */
    .stTextInput > div > div > input,
    .stTextInput > div > div > input:focus {
        background-color: rgba(30, 41, 59, 0.6) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 10px;
    }
    
    .stSelectbox > div > div > div {
        background-color: rgba(30, 41, 59, 0.6);
        color: #f1f5f9;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }

    /* Headings - Solid White */
    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 700;
    }
    
    h1 {
        font-size: 2.5rem;
        letter-spacing: -0.02em;
    }
    
    h2 {
        color: #e0e7ff !important;
    }
    
    h3 {
        color: #e0e7ff !important;
    }

    /* Streamlit Native Elements */
    .stMetric label {
        color: #cbd5e1 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #22d3ee !important;
    }
    
    /* Text Elements */
    p, span, div {
        color: #e5e7eb;
    }
    
    .stMarkdown {
        color: #e5e7eb;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.4);
        color: #f1f5f9 !important;
        border-radius: 8px;
    }

    /* Status/Success Messages */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1);
        color: #86efac !important;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        color: #fca5a5 !important;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .stInfo {
        background-color: rgba(59, 130, 246, 0.1);
        color: #93c5fd !important;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0e1a;
    }
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
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

# Fixed: Use env var if available
env_key = os.getenv("GEMINI_API_KEY")

with st.expander("AI設定", expanded=not bool(env_key)):
    if env_key:
        st.success("🔐 APIキーが設定されています (環境変数: GEMINI_API_KEY)")
        api_key = env_key
    else:
        api_key = st.text_input("Google Gemini APIキーを入力", type="password", help="aistudio.google.com で無料キーを取得できます")
    
    # AI Model Selection
    model_options = [
        "gemini-3-pro-preview",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-pro-exp-02-05",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]
    selected_model = st.selectbox("使用するAIモデルを選択", options=model_options, index=0)

if st.button("🚀 AIリサーチ開始"):
    if not api_key:
        st.error("有効なAPIキーを入力してください。")
    else:
        from logic.ai_researcher import AIResearcher
        
        researcher = AIResearcher(api_key)
        
        with st.status("🤖 AIが調査中...", expanded=True) as status:
            st.write("🔍 Google検索を実行し、最新の市場ニュースを収集しています...")
            st.write("🧠 厳格な基準で分析・選定中...")
            
            # analyze_with_gemini now reads prompt.txt and takes selected_model
            ai_results = researcher.analyze_with_gemini(selected_model=selected_model)
            
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



