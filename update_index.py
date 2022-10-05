# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 21:28:46 2022

@author: uest
"""

#%%
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt

import akshare as ak
from tqdm import tqdm
import plotly
import plotly.express as px
# import warnings
# warnings.filterwarnings("ignore")
#%%
def get_df(look_back=63):
    temp = ak.sw_index_spot()
    a = list(temp['指数代码'])
    b = list(temp['指数名称'])
    temp = zip(a, b)
    symbol_name = {}
    for symbol, name in temp:
        symbol_name[symbol] = [name]

    for symbol in tqdm(symbol_name.keys()):
        df = ak.index_level_one_hist_sw(symbol)[['指数代码', '发布日期', '收盘指数', '平均流通市值']]
        df.columns = ['code', 'date', 'close', 'value']
        df = df.iloc[-(look_back+1):]    
        date = df['date'].iloc[-1]
        ret = round(df['close'].pct_change(look_back).iloc[-1], 4)
        value = round(df['value'].mean(), 2)
        symbol_name[symbol] += [date, ret, value]
        
    df = pd.DataFrame({'code':symbol_name.keys()})
    df[['name', 'date', 'return', 'value']] = np.nan
    for i in range(len(df)):
        df.loc[i, ['name', 'date', 'return', 'value']] = symbol_name[df.loc[i]['code']]

    df['return_display'] = df['return'].apply(lambda x: format(x, '.2%')) 
    assert len(df['date'].unique()) == 1
    
    return df
#%%
LOOK_BACK = 126
df = get_df(LOOK_BACK)
df.head()
#%%
fig = px.treemap(data_frame=df, 
                 path=[px.Constant('申万一级行业指数'), 'name'], 
                 values='value',
                 color='return', 
                 # hover_data=['return', 'return_display'],
                 custom_data=['return_display'],
#                  title='{}, 近{}日涨跌幅'.format(df['date'][0], LOOK_BACK),
                 color_continuous_scale=['#00FF00', '#000000', '#FF0000'],
                 color_continuous_midpoint=0)

fig.data[0].texttemplate = '%{label}<br>%{customdata[0]}'
fig.update_traces(textposition="middle center")

# fig.update_traces(textinfo='label+text',textfont = dict(size = 12))
# plotly.offline.plot(fig, filename='index_return.html') 
# fig.show()
#%%
dt_string = 'temp1'
timezone_string = 'temp2'
with open('index.html', 'a') as f:
    f.truncate(0) # clear file if something is already written on it
    title = "<h1>申万一级行业</h1>"
    updated = "<h2>Last updated: " + dt_string + " (Timezone: " + timezone_string + ")</h2>"
    description = "This dashboard is updated every half an hour with sentiment analysis performed on latest scraped news headlines from the FinViz website.<br><br>"
    code = """<a href="https://medium.com/datadriveninvestor/use-github-actions-to-create-a-live-stock-sentiment-dashboard-online-580a08457650">Explanatory Article</a> | <a href="https://github.com/damianboh/dow_jones_live_stock_sentiment_treemap">Source Code</a>"""
    author = """ | Created by nn, check out my <a href="https://chenpnn.github.io/">GitHub Page</a>"""
    f.write(title + updated + description + code + author)
    f.write(fig.to_html())
    #f.write(fig.to_html(full_html=False, include_plotlyjs='cdn')) # write the fig created above into the html file
