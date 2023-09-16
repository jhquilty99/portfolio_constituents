import re
import pandas as pd
import yfinance as yf
import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd

def drop_trailing_period(string):
    return string[:-1] if string.endswith('.') else string

def get_title(html_string):
    match = re.search(r'title=\"(.*?)(?=[\"\/].)', html_string)
    if match:
        return drop_trailing_period(match.group(1))
    else:
        return drop_trailing_period(html_string)
    
def weight_to_float(value):
    if value == 'NaN':
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
    
def get_security_data(key):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
    }
    url = 'https://www.zacks.com/funds/etf/{}/holding'
    with requests.Session() as req:
        req.headers.update(headers)
        return(req.get(url.format(key)).text)

    
def scrape_security_data(keys):
    df = pd.DataFrame()
    for key in keys:
        r = get_security_data(key)
        soup = BeautifulSoup(r, 'html.parser')
        #table = soup.find(id='dataTables_scroll')
        script_text = soup.find('script', string=re.compile('etf_holdings.formatted_data'))
        script_text = str(script_text)
        #print(script_text)
        json_text = re.search('\[.*?\] ]', script_text)
        data = pd.read_json(json_text.group())
        data['clean_name'] = data[0].apply(get_title)
        data['weight'] = data.apply(lambda x: weight_to_float(x[3]), axis = 1)
        data['etf'] = key
        df = pd.concat([data[['clean_name','weight','etf']],df])
    df.drop_duplicates(inplace = True)
    return(df)

def get_current_prices(keys):
    data = yf.download(keys, period="1d", interval="1d")['Close']
    if len(keys) == 1:
        data.index = keys 
        return(data)
    else:
        return(data.iloc[0].squeeze())

def get_prop_value(portfolio, prices):
    values = pd.Series(portfolio)*prices
    total = values.sum()
    return(values/total)

def get_portfolio_prop(portfolio):
    data = get_current_prices(list(portfolio.keys()))
    return(get_prop_value(portfolio, data))

# def aggregate_weights(consituents_df, ticker_props):
#     consituents_df['portfolio_weight'] = consituents_df['etf'].apply(lambda x: ticker_props[x])
#     consituents_df['total_weight'] = consituents_df['weight'] * consituents_df['portfolio_weight']
#     return(consituents_df[['clean_name','portfolio_weight']])

# # Multiply prop of each ETF by the weight, then group by to sum up by constituent
# def get_constituent_weights(consituents_df, ticker_props):
#     df = aggregate_weights(consituents_df, ticker_props)
#     df = get_prop_value()
#     return(df.groupby(['clean_name']).sum().sort_values('portfolio_weight', ascending = False))

def get_constituent_weights(constituents, proportions):
    # Multiply the weight of each constituent by the proportion of its ETF
    constituents['adjusted_weight'] = constituents.apply(lambda row: row['weight'] * proportions[row['etf']], axis=1)
    
    # Group by 'clean_name' and sum the 'adjusted_weight' to get the total weight for each constituent
    result = constituents.groupby('clean_name')['adjusted_weight'].sum()
    total = result.sum()
    return (result/total)