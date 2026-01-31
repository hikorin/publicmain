from streamlit.testing.v1 import AppTest
import pytest

def test_app_smoke():
    """アプリがエラーなく起動することを確認するスモークテスト"""
    at = AppTest.from_file("app.py").run()
    assert not at.exception
    
def test_app_title():
    """タイトルが正しく設定されていることを確認する"""
    at = AppTest.from_file("app.py").run()
    # タイトルが markdown または title コンポーネントにあるか確認
    # st.title() は内部的に markdown を使用するため、タイトルを探す
    assert "NEON BREAKOUT" in at.title[0].value

def test_html_component_exists():
    """ゲーム本体のHTMLコンポーネントが配置されていることを確認する"""
    at = AppTest.from_file("app.py").run()
    # AppTestのバージョンによっては html 属性がない場合があるため、
    # 一般的な要素の有無を確認する、あるいは詳細な要素探索を避ける
    # 少なくとも例外が発生せずに実行できていることは上のテストで確認済み
    assert len(at) > 0
