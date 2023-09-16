import pytest
import datetime
import pandas as pd
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html
import plotly.express as px
from sqlalchemy import create_engine
import server.callback_functions as callback_functions

class TestClass:
    local_engine = create_engine('sqlite:///assets/financial_website.db')

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, fixture_setup, request):
        dates = pd.date_range(datetime.date(2022, 8, 15),periods=5, freq='D')
        input_fact_ticker_df = pd.DataFrame({
                                'price':[899.55, 905.40, 892.98, 895.41, 877.05, 5762.01, 5762.10, 5712.29, 5719.7, 5625.58],
                                'name':['Stock','Stock','Stock','Stock','Stock','Bond','Bond','Bond','Bond','Bond'],
                                },
                                index = dates.append(dates))
        input_fact_inflation_df = pd.DataFrame({
                                'value':[100, 110, 120, 130, 140, 150, 160, 170, 180, 190],
                                'name':['CPI','CPI','CPI','CPI','CPI','CPI','CPI','CPI','CPI','CPI'],
                                },
                                index = pd.date_range(datetime.date(2022, 1, 1),periods=10, freq='M'))
        with self.local_engine.begin() as con:
            input_fact_ticker_df.to_sql('fact_ticker_data', con, index = True, index_label = 'date', if_exists = 'replace', method = 'multi')
            input_fact_inflation_df.to_sql('fact_inflation_data', con, index = True, index_label = 'date', if_exists = 'replace', method = 'multi')
        print('ETL.setup')

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

    # Function - Takes the current state of the UI and creates the right graph data
    # Input - Graph down selections
    # Output - The data behind a stacked or line chart possibly adjusted for inflation
    # [] - Return portfolio values unedited
    # ['stack'] - Return portfolio values without inflation data
    # ['normal'] - Return all portfolio values normalized to the correct time frame
    # ['inflation'] - Return all portfolio values adjusted by inflation in the correct time frame
    # ['stack','normal'] - Return portfolio values without inflation data, and normalized to the correct time
    # ['normal','inflation'] - Get all inflation adjusted portfolio values and normalize them to the right time
    # ['inflation','stack'] - Return all portfolio values adjusted by inflation in the correct time frame and inflation dropped
    # ['stack','normal','inflation'] - Get all inflation adjusted portfolio values and normalize them to the right time and inflation dropped
    def test_get_figure_data(self):
        test_portfolio = {'Stock':5,'Bond':5}
        dates = pd.date_range(datetime.date(2022, 8, 15),periods=5, freq='D')
        output = callback_functions.get_figure_data(test_portfolio, [datetime.date(2022, 8, 15), datetime.date(2022, 8, 20)], None)
        test = pd.DataFrame({
                                'price':[899.55*5, 905.40*5, 892.98*5, 895.41*5, 877.05*5, 5762.01*5, 5762.10*5, 5712.29*5, 5719.7*5, 5625.58*5],
                                'name':['Stock','Stock','Stock','Stock','Stock','Bond','Bond','Bond','Bond','Bond'],
                                },
                                index = dates.append(dates))
        pd.testing.assert_frame_equal(test, output, check_names = False, check_freq = False)
        
        
        
        

    # Function - Takes the current state of the UI and creates the right graph based on the financial data
    # Input - Portfolio values data, range and graph down selections
    # Output - Either a stacked or line chart possibly adjusted for inflation
    def test_draw_figure(self):
        test_portfolio = {'Stock':5,'Bond':5}
        cash = 1000
        portfolio_values = 0
        figure = callback_functions.draw_figure([], callback_functions.get_figure_data([], portfolio_values, 5), range)
        assert type(figure) == type(px.line())

        figure = callback_functions.draw_figure(['stack'], callback_functions.get_figure_data(['stack'], portfolio_values, 5), range)
        assert type(figure) == type(px.area())

        figure = callback_functions.draw_figure(['normal'], callback_functions.get_figure_data(['normal'], portfolio_values, 5), range)
        assert type(figure) == type(px.line())

        figure = callback_functions.draw_figure(['inflation'], callback_functions.get_figure_data(['inflation'], portfolio_values, 5), range)
        assert type(figure) == type(px.line())

        figure = callback_functions.draw_figure(['stack','normal'], callback_functions.get_figure_data(['stack','normal'], portfolio_values, 5), range)
        assert type(figure) == type(px.area())

        figure = callback_functions.draw_figure(['normal','inflation'], callback_functions.get_figure_data(['normal','inflation'], portfolio_values, 5), range)
        assert type(figure) == type(px.line())

        figure = callback_functions.draw_figure(['inflation','stack'], callback_functions.get_figure_data(['inflation','stack'], portfolio_values, 5), range)
        assert type(figure) == type(px.area())

        figure = callback_functions.draw_figure(['inflation','normal','stack'], callback_functions.get_figure_data(['inflation','normal','stack'], portfolio_values, 5), range)
        assert type(figure) == type(px.area())
        


    # Function - Returns the correct offset for the selected timing
    # Input - End date, portfolio tickers as a list, and the range selection
    # Output - Range of selected days and offset days from today, excluding market holidays
    def test_get_range(self):
        date = datetime.date(2022, 8, 19)
        assert callback_functions.get_range(['VGT'],'all', date)[0] == [pd.Timestamp(datetime.datetime(2019,8,21)), pd.Timestamp(datetime.datetime(2022, 8, 19))]
        assert callback_functions.get_range(['VGT'],'all', date)[1] == 756
        assert callback_functions.get_range(['VGT'],'one month', date)[0] == [pd.Timestamp(datetime.datetime(2022,7,19)), pd.Timestamp(datetime.datetime(2022, 8, 19))]
        assert callback_functions.get_range(['VGT'],'one month', date)[1] == 24 
        assert callback_functions.get_range(['VGT'],'three months', date)[0] == [pd.Timestamp(datetime.datetime(2022,5,19)), pd.Timestamp(datetime.datetime(2022, 8, 19))]
        assert callback_functions.get_range(['VGT'],'three months', date)[1] == 64
        assert callback_functions.get_range(['VGT'],'one year', date)[0] == [pd.Timestamp(datetime.datetime(2021,8,19)), pd.Timestamp(datetime.datetime(2022, 8, 19))] 
        assert callback_functions.get_range(['VGT'],'one year', date)[1] == 253
        assert callback_functions.get_range(['VGT'],'ytd', date)[0] == [pd.Timestamp(datetime.datetime(2022,1,3)), pd.Timestamp(datetime.datetime(2022, 8, 19))]
        assert callback_functions.get_range(['VGT'],'ytd', date)[1] == 159 
        assert callback_functions.get_range(['VGT','EDV'],'all', date)[0] == [pd.Timestamp(datetime.datetime(2019,8,21)), pd.Timestamp(datetime.datetime(2022, 8, 19))]
        assert callback_functions.get_range(['VGT','EDV'],'all', date)[1] == 756
        assert callback_functions.get_range(['VGT','EDV'],'one month', date)[0] == [pd.Timestamp(datetime.datetime(2022,7,19)), pd.Timestamp(datetime.datetime(2022, 8, 19))]
        assert callback_functions.get_range(['VGT','EDV'],'one month', date)[1] == 24 
        assert callback_functions.get_range(['VGT','EDV'],'three months', date)[0] == [pd.Timestamp(datetime.datetime(2022,5,19)), pd.Timestamp(datetime.datetime(2022, 8, 19))]
        assert callback_functions.get_range(['VGT','EDV'],'three months', date)[1] == 64
        assert callback_functions.get_range(['VGT','EDV'],'one year', date)[0] == [pd.Timestamp(datetime.datetime(2021,8,19)), pd.Timestamp(datetime.datetime(2022, 8, 19))] 
        assert callback_functions.get_range(['VGT','EDV'],'one year', date)[1] == 253
        assert callback_functions.get_range(['VGT','EDV'],'ytd', date)[0] == [pd.Timestamp(datetime.datetime(2022,1,3)), pd.Timestamp(datetime.datetime(2022, 8, 19))]
        assert callback_functions.get_range(['VGT','EDV'],'ytd', date)[1] == 159 

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

    # Function - Pulls relevant stored portfolio information from yaml config
    # Input - Yaml config file with portfolio parameters
    # Output - Portfolio parameters 
    def test_collect_yaml(self):
        portfolio = callback_functions.collect_yaml('testing_portfolio.yml')
        assert portfolio == ["VGT","EDV","GME"]