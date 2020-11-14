import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import datetime as dtime
from datetime import datetime as dt
import plotly.figure_factory as ff
import plotly.graph_objects as go
import cufflinks as cf
import sqlite3
import dash_dangerously_set_inner_html as ds
from datetime import datetime,timedelta
import pandas as pd
from datashop.datashop import df_scaler
from datashop.datashop import min_max_col
import dash_table
import dash_bootstrap_components as dbc
import json

###################################             pseudo-css

tab_style = {
    'backgroundColor': '#1f1e1e',
    'font-family': 'Impact, Haettenschweiler, Arial Narrow Bold, sans-serif',
    'color':'#586069',
    'padding': '20px',
    'font-family': 'Impact, Haettenschweiler, Arial Narrow Bold, sans-serif',
    'font-size': 'x-large',
    'display': 'flex',
    'align-items': 'center',
    'justify-content': 'center',
    'border-style': 'none'

}

sel_tab = {
    'backgroundColor': ' #cecccc ',
    'color':'#586069',
    'border-top-left-radius': '5px',
    'border-top-right-radius': '5px',
    'padding': '20px',
    'font-family': 'Impact, Haettenschweiler, Arial Narrow Bold, sans-serif',
    'font-size': 'x-large',
    'display': 'flex',
    'align-items': 'center',
    'justify-content': 'center',
    'border-style': 'none'

}

##############   Title Div

title = '''

# The Energy Dashboard

'''


title_div = html.Div(
    children = [dcc.Markdown(title)],
    id='title_div',
    )

################################                    First Tab


welcome = 'Welcome to the Energy Dashboard!'

mn_text = """ 
    
    Your one stop shop for the latest petroleum related news and information!
    
    Click the tabs above to explore.


    
    
    ### Report:
    ---
    All the latest news, price data, inventory levels and other juicy data. 
      
        
          

 
    ### Chart:
    ---
    A visualization tool to examine trends and corelations in important 
    petroleium related datasets.

    Multiple series can be plotted at once. 
    
    All data will be scaled from 0 to 1 to make 
    comparisons easier. 

    Available series include:  

    *Daily Price*  
      
    *Weekly Inventory Level*  
      
    *Consumptions*  
      
    *DOW Jones Industrial Average*  
      
    *News Headlines*  
      
    ### Map
    ---

      
      A map showing regional proudction levels and gas prices



"""

welcome = html.Div(welcome, id = 'welc_span')
body = dcc.Markdown(children=mn_text, id='welc_body')

welcome_tab=html.Div(
            children = [
                    welcome,
                    body
                    ],
            id='main_content'
            )

##############_____________     News      _____________#######################
with open ('data/cache.json','r') as cache_file:
    cache_dict = json.load(cache_file)

conn = sqlite3.connect('data/energydash.db')



news_update = cache_dict['news_update']

query = 'SELECT date,abstract,url FROM news ORDER BY date DESC LIMIT 10'

df_news = pd.read_sql_query(query,conn)

def makelink(url):
    link = html.A(html.P('Full Article'),href=url,target = '_blank')
    return link
    
df_news['hlinks']= df_news['url'].apply(makelink)
df_news.drop('url',axis=1,inplace= True)

news_bar = html.Div(
    children=[
        html.Span(
            'Recent News',
            id='newstitle'
        ),
        html.Span(
            'Last Updated: ' + str(news_update),
            id='newsupdate'
        )
    ],
    id='newsbar'
)

news_table = dbc.Table.from_dataframe(
    df_news,
    id='newstable',
    className = 'newstable'
)

news_section = html.Div(
    children=[news_bar,news_table],
    id='newssection'
)

##___   Final Report Div
report=html.Div(
    id='reportdiv',
    children=[news_section]
)


################_____________     CHART      _____________#######################


start_date = str(datetime.now() - timedelta(90))[:10]

conn = sqlite3.connect('data/energydash.db')
c = conn.cursor()

query = '''
        SELECT Date, DailyPrice 
        FROM DailyPrice 
        WHERE DailyPrice.Date > ? 
        ORDER BY DailyPrice.Date ASC
     '''

params = (start_date,)

df = pd.read_sql_query(query,con=conn,params=params,index_col = 'Date')[start_date:]
df['DailyPrice'] = min_max_col(df['DailyPrice'])

line_colors = {
    'News':' #cecccc', 
    'DailyPrice':' #ebe8e8',
    'WeeklyStocks':'#33FF36',
    'ProductSupplied':'#A6D5FB',
    'DIA_closing':'#FFFF00'
}

news_hover = '''
    <b>%{text}</b><br><br>
    %{x}<br>
    %{hovertext}<br><br>
    <a href=%{customdata}>Full Article</a><br>
 '''

trace1 = go.Scatter(
    x = df.index,
    y = df['DailyPrice'],
    mode='lines',
    name='Daily Price',
    marker=dict(color=line_colors['DailyPrice'])
)

chart_data = [trace1]

layout = go.Layout(
    xaxis = {
        'title':'Time',
        'showgrid':False,
        'showspikes':True
        
    },
    yaxis = {
        'showgrid':False
    },
    plot_bgcolor = '#252526',
    paper_bgcolor = '#252526',
    autosize=True,
    hovermode = 'closest'
    
)

fig = go.Figure(data=chart_data,layout = layout)

checkoptions = [
    {'value':'News','label':'News'},
    {'label':'Daily Price', 'value':'DailyPrice'},
    {'label':'Weekly Stocks','value':'WeeklyStocks'},
    {'label':'Product Sold', 'value':'ProductSupplied'},
    {'label':'DOW Jones','value':'DIA_closing'}
    ]

date_selector = dcc.DatePickerRange(
            id='date_div',
            start_date=start_date,
            end_date= str(dtime.datetime.today().date()),
            min_date_allowed = dt(2000,1,1),
            className='date_div'
            )

series_selector = dcc.Dropdown(
            id='series_div',
            options=checkoptions,
            value=['DailyPrice'],
            className = 'series_div',
            multi = True
            )

gen_button = html.Button(
            'Generate',
            id='generate',
            className='gen_butt'
)



controls_div = html.Div(
    id='controls_div',
    children = [
        gen_button,           
        date_selector,
        series_selector,
        
    ]
)
graph_div = html.Div(
            id='graph_div',
            children=[
                dcc.Graph(
                    id='main-graph',
                    figure=fig,
                    animate=True)
            ]
            )

chart = [
    controls_div,
    graph_div
]

