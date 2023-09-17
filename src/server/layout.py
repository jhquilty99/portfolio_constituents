# Import necessary libraries
from dash import dcc, html, Dash, dash_table

# Initialize the Dash app
app = Dash(__name__)

TOP_STYLE = {
    'border': '1px solid black', 
    'padding': '10px', 
    'max-width': '720px', 
    'margin': '10px auto',
    'width':'100%'
}

OUTER_STYLE = {
    'display': 'flex', 
    'flex-direction': 'column', 
    'align-items': 'center',
    'width':'100%'
}

DEFAULT_TICKERS = ['VGT','EDV','QQQ']

# Define the app layout with outer container for centering
app.layout = html.Div([
    # First Section
    html.Div([
        # Title
        html.H1("Portfolio"),
        # Add to Portfolio Section
        html.Div([
            dcc.Input(
                id='enter-row-name',
                placeholder='Enter an ETF name here...',
                type='text',
                style={'padding': 10,'width':'25%'}
            ),
            dcc.Input(
                id='enter-row-amount',
                placeholder='Enter the number of shares here...',
                type='number',
                min=1,
                style={'padding': 10,'width':'49%'}
            ),
            html.Button('Add Row', id='add-row', n_clicks=0, style={'padding': 10,'width':'19%'})
        ], style={'height': 50}),
        # Portfolio Table Section
        dash_table.DataTable(
            id='ticker-table',
            columns=[
                {'name': 'Holding','id': 'ticker'},
                {'name': 'Amount', 'id':'amount'}
            ],
            data=[
                {'ticker': i, 'amount': 1} for i in DEFAULT_TICKERS
            ],
            row_deletable=True,
            cell_selectable=False
        ),
        # Save Button
        html.Br(),
        html.Button('Save Portfolio', id='save-portfolio', n_clicks=0),
    ], style=TOP_STYLE),

    # Second Section
    html.Div([
        # Title
        html.H1("Portfolio Constituents"),
        # Constituents Section
        # dcc.Dropdown(disabled=True),
        # Table Section
        html.Div(id = 'constituents-table')
    ], style=TOP_STYLE),

    # Third Section
    html.Div([
        # Title
        html.H1("Portfolio Value Distribution"),
        # Pie Graph Section
        dcc.Graph(id="pie-graph"),
    ], style=TOP_STYLE),
], style=OUTER_STYLE)