import pytest
import datetime
import pandas as pd
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html
import plotly.express as px
import server.callback_functions as callback_functions

class TestClass:

    # Function - Gets the current active tickers
    # Input - Dynamic callback from delete buttons, as a dictionary
    # Output - Unique tickers that have not been deleted, as a list
    def test_active_tickers(self):
        input = {
            '{"index":"VGT","type":"dynamic-delete"}.n_clicks': 0,
            '{"index":"BLV","type":"dynamic-delete"}.n_clicks': 0,
            '{"index":"EDV","type":"dynamic-delete"}.n_clicks': 0,
        }
        assert callback_functions.active_tickers(input) == ['VGT','BLV','EDV']
        input = {
            '{"index":"VGT","type":"dynamic-delete"}.n_clicks': 0,
            '{"index":"BLV","type":"dynamic-delete"}.n_clicks': 1,
            '{"index":"EDV","type":"dynamic-delete"}.n_clicks': 0,
        }
        assert callback_functions.active_tickers(input) == ['VGT','EDV']
        input = {
            '{"index":"VGT","type":"dynamic-delete"}.n_clicks': 1,
            '{"index":"BLV","type":"dynamic-delete"}.n_clicks': 1,
            '{"index":"EDV","type":"dynamic-delete"}.n_clicks': 0,
        }
        assert callback_functions.active_tickers(input) == ['EDV']
        input = {
            '{"index":"VGT","type":"dynamic-delete"}.n_clicks': 1,
        }
        assert callback_functions.active_tickers(input) == ['VGT']
        input = {
            '{"index":"VGT","type":"dynamic-delete"}.n_clicks': 1,
            '{"index":"BLV","type":"dynamic-delete"}.n_clicks': 1,
            '{"index":"BLV","type":"dynamic-delete"}.n_clicks': 0,
            '{"index":"EDV","type":"dynamic-delete"}.n_clicks': 0,
        }
        assert callback_functions.active_tickers(input) == ['BLV','EDV']

    # Function - Utilize portfolio to draw dynamic UI elements
    # Input - Portfolio dictionary containing the amounts of each ticker
    # Output - Nested dynamic UI elements including a numeric input and delete button for each ticker
    def test_draw_portfolio_inputs(self):
        test_portfolio = {'VGT':10,'EDV':20}
        buttons = callback_functions.draw_portfolio_inputs(test_portfolio)
        assert type(buttons) == type([])
        assert len(buttons) == 2
        assert str(buttons[0]) == str(dbc.Row(children = [
                dbc.Col(html.H4('VGT', style={'textAlign': 'center'}), width=4),
                dbc.Col(daq.NumericInput(min=0, 
                                        max=1000, 
                                        value=10, 
                                        size='fit',
                                        id = {'type':'portfolio-modification','index':'VGT'})
                        , align = 'center', width=6),
                dbc.Col(dbc.Button(className="bi bi-x-square-fill", 
                                    color="white", 
                                    style={'border-width': 0, 'font-size':30},
                                    n_clicks=0,  
                                    id = {'type':'portfolio-deletion','index':'VGT'})
                        , align='right', width=1)
            ], style={"width": "100%"}, align='center'))
        assert str(buttons[1]) == str(dbc.Row(children = [
                dbc.Col(html.H4('EDV', style={'textAlign': 'center'}), width=4),
                dbc.Col(daq.NumericInput(min=0, 
                                        max=1000, 
                                        value=20, 
                                        size='fit',
                                        id = {'type':'portfolio-modification','index':'EDV'})
                        , align = 'center', width=6),
                dbc.Col(dbc.Button(className="bi bi-x-square-fill", 
                                    color="white", 
                                    style={'border-width': 0, 'font-size':30},
                                    n_clicks=0,  
                                    id = {'type':'portfolio-deletion','index':'EDV'})
                        , align='right', width=1)
            ], style={"width": "100%"}, align='center'))

    # Function - Gets the portfolio updated from the UI when incremented
    # Input - Callback related to portfolio inputs, as a list of dictionaries
    # Output - Portfolio dictionary reflecting UI with most recent quantities
    def test_increment_portfolio(self):
        input = [
                    {
                        'id': {
                            'index': 'VGT',
                            'type': 'numeric-input'
                            },
                        'property': 'value',
                        'value': 15
                    },
                    {
                        'id': {
                            'index': 'EDV',
                            'type': 'numeric-input'
                            },
                        'property': 'value',
                        'value': 10
                    },
                    {
                        'id': {
                            'index': 'GME',
                            'type': 'numeric-input'
                            },
                        'property': 'value',
                        'value': 20
                    }
                ]
        test_portfolio = {'VGT':15,'EDV':10,'GME':20}
        assert test_portfolio == callback_functions.increment_portfolio(input)
        

    # Function - Adds distinct tickers to existing portfolio
    # Input - Current portfolio as a dictionary, distinct tickers as a list, added ticker
    # Output - Portfolio dictionary reflecting UI with new ticker, as well as the state to indicate if the ticker was added successfully 
    def test_add_ticker(self):
        test_portfolio = {'VGT':15,'EDV':15,'GME':15}
        output = callback_functions.add_ticker()
        assert output[0] == test_portfolio
        assert output[1] == False
        assert output[2] == False
        output = callback_functions.add_ticker(None, 'hhopple')
        assert output[0] == test_portfolio
        assert output[1] == False
        assert output[2] == True
        output = callback_functions.add_ticker(None, 'GME')
        assert output[0] == test_portfolio
        assert output[1] == False
        assert output[2] == False
        output = callback_functions.add_ticker(None, 'AAPL')
        test_portfolio = {'VGT':15,'EDV':15,'GME':15,'AAPL':5}
        assert output[0] == test_portfolio
        assert output[1] == True
        assert output[2] == False
        output = callback_functions.add_ticker(None, 'AAPL')
        test_portfolio = {'VGT':15,'EDV':15,'GME':15,'AAPL':5}
        assert output[0] == test_portfolio
        assert output[1] == True
        assert output[2] == False

        test_portfolio = {'VGT':15,'EDV':10,'GME':20}
        test_output = {'VGT':15,'EDV':10,'GME':20}
        output = callback_functions.add_ticker(test_portfolio, None)
        assert output[0] == test_output
        assert output[1] == False
        assert output[2] == False
        output = callback_functions.add_ticker(test_portfolio, 'GME')
        assert output[0] == test_output
        assert output[1] == False
        assert output[2] == False
        output = callback_functions.add_ticker(test_portfolio, 'hhopple')
        assert output[0] == test_output
        assert output[1] == False
        assert output[2] == True
        output = callback_functions.add_ticker(test_portfolio, 'AAPL')
        assert output[0] == {'VGT':15,'EDV':10,'GME':20,'AAPL':5}
        assert output[1] == True
        assert output[2] == False
        output = callback_functions.add_ticker(test_portfolio, 'AAPL')
        assert output[0] == {'VGT':15,'EDV':10,'GME':20,'AAPL':5}
        assert output[1] == True
        assert output[2] == False
    

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