from dash.dependencies import Input, Output, State, ALL, MATCH
import callback_functions
from layout import app
from dash import callback_context

################# Ticker State Machine #################
# Inputs: Dynamic Delete Buttons
# Outputs: Distinct Tickers
@app.callback(
    Output('distinct-tickers','data'),
    Input({'type':'portfolio-deletion','index':ALL},"n_clicks"),
    prevent_initial_call=True
)
def get_active_tickers(portfolio_deletion):
    return(callback_functions.active_tickers(callback_context.inputs))
    

################# Button State Machine #################
# Inputs: Distinct Tickers, Portfolio Buffer, Add Ticker Form
# Outputs: Dynamic Increment Buttons, Dynamic Delete Buttons, Valid or Invalid Add Form
@app.callback(
    Output('dynamic-ticker-buttons','children'),
    Output('add-ticker', "valid"),
    Output('add-ticker', "invalid"),
    Input('portfolio-buffer','data'),
    Input('distinct-tickers','data'),
    Input('add-ticker','value')
)
def dynamic_portfolio_update(portfolio_buffer, distinct_tickers, new_ticker):
    new_portfolio, true_validation, false_validation = callback_functions.add_ticker(portfolio_buffer, distinct_tickers, new_ticker)
    return(callback_functions.draw_portfolio_inputs(new_portfolio), true_validation, false_validation)

################# Portfolio State Machine ##############
# Inputs: Dynamic Increment Inputs
# Outputs: Portfolio Buffer
@app.callback(
    Output('portfolio-buffer','data'),
    Input({'type':'portfolio-modification','index':ALL},"value"),
    prevent_initial_call=True
)
def increment_portfolio(dynamic_ticker_values):
    return(callback_functions.increment_portfolio(callback_context.inputs_list[0]))

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)