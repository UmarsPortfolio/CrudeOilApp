import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
from datetime import datetime as dt
import plotly
import plotly.graph_objs as go
import cufflinks as cf
import sqlite3
import dash_dangerously_set_inner_html as ds

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

