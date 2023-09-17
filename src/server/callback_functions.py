import pandas as pd
import yfinance
import re
from src.analysis.data_pull import get_security_data

pd.options.display.float_format = '{:6.2f}'.format
 
def validate_stock(ticker: str) -> bool:
    info = yfinance.Ticker(ticker).history(period='7d', interval='1d')
    try:
        security_text = get_security_data(ticker)
        if re.search('Zacks ETF Rank', security_text) is None:
            return False
    except:
        return False
    return len(info) > 0