import re
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_title(html_string):
    match = re.search(r'title=\"(.*?)(?=\.)', html_string)
    if match:
        return match.group(1)
    else:
         return(html_string)
    
def weight_to_float(value):
    if value != 'NA': 
        return float(value) 
    else: 
        return 0
    
def scrape_security_data(keys):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
    }
    url = 'https://www.zacks.com/funds/etf/{}/holding'
    df = pd.DataFrame()
    with requests.Session() as req:
        req.headers.update(headers)
        for key in keys:
            r = req.get(url.format(key))
            soup = BeautifulSoup(r.text, 'html.parser')
            #table = soup.find(id='dataTables_scroll')
            script_text = soup.find('script', string=re.compile('etf_holdings.formatted_data')).string
            json_text = re.search('\[.*?\] ]', script_text)
            #data = json.loads(json_text.group())
            data = pd.read_json(json_text.group())
            data['clean_name'] = data.apply(lambda x: get_title(str(x[0])), axis = 1)
            data['weight'] = data.apply(lambda x: weight_to_float(x[3]), axis = 1)
            data['etf'] = key
            df = pd.concat([data[['clean_name','weight','etf']],df])
    df.drop_duplicates(inplace = True)
    return(df)

def get_prop_of_each_etf(portfolio):
    data = yf.download(list(portfolio.keys()), period="1d", interval="1d")['Close']
    data.iloc[0,:]
    values = pd.Series(portfolio)*data.iloc[0,:]
    total = values.sum()
    return(values/total)

# Multiply prop of each ETF by the weight, then group by to sum up by constituent
def get_constituent_weights(consituents_df, ticker_proportions):
    consituents_df['portfolio_weight'] = consituents_df.apply(lambda x: ticker_proportions[x['etf']], axis = 1)
    consituents_df['total_weight'] = consituents_df['weight'] * consituents_df['portfolio_weight']
    consituents_df = consituents_df[['clean_name','portfolio_weight']]
    return(consituents_df.groupby(['clean_name']).sum().sort_values('portfolio_weight', ascending = False))