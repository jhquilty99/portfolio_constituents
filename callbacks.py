from dash.dependencies import Input, Output, State, ALL, MATCH
from src.server.callback_functions import validate_stock
from src.analysis.data_pull import get_current_prices, get_constituent_weights, get_prop_value, scrape_security_data
from src.server.layout import app, OUTPUT_LAYOUT_INITIAL, output_layout_final
import pandas as pd

@app.callback(
    Output('ticker-table', 'data'),
    Output('ticker-validation','children'),
    Input('add-row', 'n_clicks'),
    State('enter-row-name', 'value'),
    State('enter-row-amount', 'value'),
    State('ticker-table', 'data'))
def update_rows(n_clicks, name, amount, existing_rows):
    if n_clicks > 0: 
        if validate_stock(name):
            for i, row in enumerate(existing_rows):
                if row['ticker'] == name:
                    existing_rows[i] = {'ticker': name, 'amount': row['amount'] + int(amount)}
                    return (existing_rows, f'Added {amount} shares to {name}.')
            existing_rows.append({'ticker': name, 'amount': int(amount)})
            return (existing_rows, f'Added new ticker {name}, with {amount} shares.')
        else: 
            return (existing_rows, f'Could not find data for {name}.')
    return (existing_rows, None)

@app.callback(#Output('constituents-table', 'children'),
              #Output('pie-graph', 'figure'),
              Output('output-layout', 'children'),
              Input('save-portfolio','n_clicks'),
              State('ticker-table', 'data'),
              prevent_initial_call = False)
def display_output(n_clicks, rows):
    if n_clicks > 0:
        portfolio = pd.DataFrame(rows)
        prices = get_current_prices(list(portfolio['ticker']))
        formatted_portfolio = portfolio.set_index('ticker')['amount'].to_dict()
        prop = get_prop_value(formatted_portfolio, prices)
        consts = scrape_security_data(list(portfolio['ticker']))
        consts_df = get_constituent_weights(consts, prop).reset_index()
        consts_df.columns = ['name', 'value']
        #df['value'] = df['value']*100
        #df['value'] = df['value'].apply("{:,.2f}%".format)
        portfolio['result'] = portfolio['ticker'].map(prices) * portfolio['amount']
        portfolio['result'] = portfolio['result'].apply(round, ndigits = 2)
        portfolio['result_formatted'] = portfolio['result'].apply("${:,.2f}".format)
        return output_layout_final(consts_df, portfolio)
    else:
        return OUTPUT_LAYOUT_INITIAL

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)