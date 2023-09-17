import pytest
import datetime
import pandas as pd
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html
import plotly.express as px
import src.server.callback_functions as callback_functions

class TestClass:
    # Function - Identifies if a stock is in the yahoo finance market
    # Input - Ticker input by user, as a string
    # Output - Boolean concerning its presence in the stock market
    def test_validate_stock(self):
        assert callback_functions.validate_stock("VGT") == True
        assert callback_functions.validate_stock("MSFT") == True
        assert callback_functions.validate_stock("BLV") == True
        assert callback_functions.validate_stock("asdssadasda") == False
        assert callback_functions.validate_stock("") == False
        assert callback_functions.validate_stock("VgT") == True