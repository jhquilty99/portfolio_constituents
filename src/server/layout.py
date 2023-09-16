# Import necessary libraries
from dash import dcc, html, Dash
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = Dash(__name__)

TOP_STYLE = {
    'border': '1px solid black', 
    'padding': '10px', 
    'max-width': '600px', 
    'margin': '10px auto',
    'width':'100%'
}

# Define the app layout
app.layout = html.Div([
    # Outer container for centering
    html.Div([
        # First section
        html.Div([
            html.H1("Portfolio"),
            dbc.Card([
                dbc.FormFloating([
                    dbc.Input(id='add-ticker'),
                    dbc.Label("Add a new ticker here..."),
                    dbc.FormFeedback("A new ticker has been added", type="valid"),
                    dbc.FormFeedback("This does not look like a valid ticker, try again",type="invalid")
                ]),
                html.Div(id='dynamic-ticker-buttons'),
            ], body = True), 
            html.Br(), 
            # Add any other components or content you want in the first section here
        ], style=TOP_STYLE),

        # Second section
        html.Div([
            html.H1("Constituents"),
            dcc.Dropdown(
                id='consts-dropdown',
                options=[
                    {'label': 'VGT', 'value': 'VGT'},
                    {'label': 'EDV', 'value': 'EDV'},
                    {'label': 'Portfolio', 'value': 'Portfolio'},
                ],
                value='Portfolio'  # default value
            ),
            # Add any other components or content you want in the second section here
        ], style=TOP_STYLE)
    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
    # Storage
    dcc.Store(id="distinct-tickers"),
    dcc.Store(id="portfolio-buffer"),
])
