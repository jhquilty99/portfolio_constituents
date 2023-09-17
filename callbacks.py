from dash.dependencies import Input, Output, State, ALL, MATCH
from src.server.callback_functions import validate_stock
from src.analysis.data_pull import get_current_prices, get_constituent_weights, get_prop_value, scrape_security_data
from src.server.layout import app
import plotly.express as px
import pandas as pd
import dash_ag_grid as dag

@app.callback(
    Output('ticker-table', 'data'),
    Input('add-row', 'n_clicks'),
    State('enter-row-name', 'value'),
    State('enter-row-amount', 'value'),
    State('ticker-table', 'data'))
def update_rows(n_clicks, name, amount, existing_rows):
    if n_clicks > 0 and validate_stock(name):
        for i, row in enumerate(existing_rows):
            if row['ticker'] == name:
                existing_rows[i] = {'ticker': name, 'amount': row['amount'] + int(amount)}
                return existing_rows
        existing_rows.append({'ticker': name, 'amount': int(amount)})
    return existing_rows

@app.callback(Output('constituents-table', 'children'),
              Output('pie-graph', 'figure'),
              Input('save-portfolio','n_clicks'),
              State('ticker-table', 'data'),
              prevent_initial_call = True)
def display_output(n_clicks, rows):
    if n_clicks > 0:
        portfolio = pd.DataFrame(rows)
        prices = get_current_prices(list(portfolio['ticker']))
        formatted_portfolio = portfolio.set_index('ticker')['amount'].to_dict()
        prop = get_prop_value(formatted_portfolio, prices)
        consts = scrape_security_data(list(portfolio['ticker']))
        df = get_constituent_weights(consts, prop).reset_index()
        df.columns = ['name', 'value']
        df['value'] = df['value'].apply("{:,.4f}%".format)
        constituents_table = dag.AgGrid(
            rowData=df.to_dict("records"),
            columnDefs=[{"field": i, "sortable": True} for i in df.columns],
        )
        portfolio['result'] = portfolio['ticker'].map(prices) * portfolio['amount']
        portfolio['result'] = portfolio['result'].apply(round, ndigits = 2)
        portfolio['result_formatted'] = portfolio['result'].apply("${:,.2f}".format)
        output_graph = px.pie(portfolio, names='ticker', values='result', hover_data=['result_formatted'], hole=0.3)
    return (constituents_table, output_graph)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)