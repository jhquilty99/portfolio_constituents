# Import necessary libraries
from dash import dcc, html, Dash, dash_table
import dash_bootstrap_components as dbc
from flask import Flask
import dash_ag_grid as dag
import plotly.express as px

#Instantiates the Dash app and identify the server
server = Flask(__name__)
app = Dash(__name__, 
           server = server, 
           title='Climate Visualizer', 
           external_stylesheets=[dbc.themes.COSMO, dbc.icons.BOOTSTRAP], 
           suppress_callback_exceptions=True)

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

INTRO_TEXT = '''
    This website is intended to pull the aggregate 
    holdings of all your etfs together into one view. 
    You can add new ETFs or increase the holdings of current ETFs in the portfolio by
    using the forms to enter the ticker and shares, and then click 'Submit.' 
    You can also remove ETFs by clicking the 'X' button next to their name.
    When you're done setting the portfolio, click 'Save Portfolio' to visualize the 
    distribution of underlying holdings in your ETFs.
'''

DEFAULT_TICKERS = ['VGT','EDV','QQQ']


OUTPUT_LAYOUT_INITIAL = [
    html.P('Visualize ETF distribution here, after clicking "Save Portfolio"', 
           style={
                'padding': '10px', 
                'max-width': '720px', 
                'margin': '10px auto',
                'width':'100%'
            })
]

def output_layout_final(constituents_df, portfolio_df):
    return([
        # Second Section
        html.Div([
            # Title
            html.H1("Portfolio Constituents"),
            # Constituents Section
            # dcc.Dropdown(disabled=True),
            # Table Section
            html.Br(),
            dag.AgGrid(
                rowData=constituents_df.to_dict("records"),
                columnDefs=[
                    {"field": 'name', "sortable": True, "unSortIcon": True},
                    {"field": 'value', "sortable": True, "sort":"desc", 
                    "unSortIcon": True, "valueFormatter": {"function": "d3.format(',.1%')(params.value)"}}],
                columnSize="sizeToFit"
        ),
        ], style=TOP_STYLE),

        # Third Section
        html.Div([
            # Title
            html.H1("Portfolio Value Distribution"),
            # Pie Graph Section
            dcc.Graph(figure = px.pie(
                portfolio_df, names='ticker', values='result', 
                hover_data=['result_formatted'], hole=0.3
            )),
        ], style=TOP_STYLE)
    ])

# Define the app layout with outer container for centering
app.layout = html.Div([
    # First Section
    html.Div([
        # Title
        html.H1("Portfolio"),
        html.P(INTRO_TEXT, style={"fontSize": "12px"}),
        # Add to Portfolio Section
        html.Div([
            dcc.Input(
                id='enter-row-name',
                placeholder='ETF name here...',
                type='text',
                style={'padding': 10,'width':'30%'}
            ),
            dcc.Input(
                id='enter-row-amount',
                placeholder='# of shares here...',
                type='number',
                min=1,
                style={'padding': 10,'width':'40%'}
            ),
            dbc.Button("Submit", id='add-row', n_clicks=0, 
                       className="d-md-flex", style={'padding': 10,'width':'20%'})
        ], style={'height': 50, 'display': 'flex', 
                  'alignItems': 'center', 'justifyContent': 'space-between'}),
        html.Br(),
        dbc.Spinner(html.Div(id='ticker-validation')),
        html.Br(),
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
            cell_selectable=False,
            style_data={'alignItems': 'center'}
        ),
        # Save Button
        html.Br(),
        dbc.Button('Save Portfolio', id='save-portfolio', 
                   n_clicks=0, className="w-100"),
    ], style=TOP_STYLE),
    html.Div(id = 'output-layout', style={'width':'100%'})
], style=OUTER_STYLE)