import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from logic.stock_data import StockData
from logic.scorer import Scorer

# --- Mock Data ---

@pytest.fixture
def mock_stock_data():
    stock = StockData("7203.T")
    stock.ticker = MagicMock()
    return stock

def test_check_volume_surge(mock_stock_data):
    # Mock history data
    dates = pd.date_range(start="2023-01-01", periods=10)
    data = {
        'Open': [100]*10, 'High': [110]*10, 'Low': [90]*10, 'Close': [105]*10,
        'Volume': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 5000] # Last one is huge
    }
    mock_stock_data.hist = pd.DataFrame(data, index=dates)
    
    # 5-day avg before last = 1000. Last = 5000. 5000 >= 1500 (1.5x). Should be True.
    assert mock_stock_data.check_volume_surge() == True

    # No surge case
    data['Volume'] = [1000]*10
    mock_stock_data.hist = pd.DataFrame(data, index=dates)
    assert mock_stock_data.check_volume_surge() == False

def test_calculate_rsi(mock_stock_data):
    # Create price increasing sequence
    dates = pd.date_range(start="2023-01-01", periods=20)
    close_prices = np.linspace(100, 200, 20) # Constantly increasing
    data = {'Close': close_prices, 'Volume': [1000]*20}
    mock_stock_data.hist = pd.DataFrame(data, index=dates)

    rsi = mock_stock_data.calculate_rsi()
    assert rsi is not None
    assert rsi > 70 # Should be very high since it's only going up

def test_scorer_short_term(mock_stock_data):
    # Setup mocks for stock_data methods used in scorer
    mock_stock_data.calculate_beta = MagicMock(return_value=1.5) # > 1.2 (+40)
    mock_stock_data.calculate_rsi = MagicMock(return_value=25.0) # <= 30 (+30)
    mock_stock_data.check_volume_surge = MagicMock(return_value=True) # (+30)

    scorer = Scorer(mock_stock_data)
    result = scorer.evaluate_short_term()

    assert result['score'] == 100
    assert result['beta'] == 1.5
    assert result['rsi'] == 25.0
    assert result['volume_surge'] == True

def test_scorer_medium_term(mock_stock_data):
    # Setup mocks for fundamentals
    mock_stock_data.get_fundamentals = MagicMock(return_value={
        "roe": 0.15, # >= 0.10 (+25)
        "per": 10.0, # <= 15 (+25)
        "revenue_growth": 0.08, # >= 0.05 (+25)
        "total_equity": 500,
        "total_assets": 1000
    })
    # Equity ratio = 0.5 >= 0.40 (+25)
    
    scorer = Scorer(mock_stock_data)
    result = scorer.evaluate_medium_term()

    assert result['score'] == 100
    assert result['roe'] == 0.15
