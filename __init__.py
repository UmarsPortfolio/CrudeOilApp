import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
from datetime import datetime as dt
import plotly
import plotly.graph_objs as go
import cufflinks as cf
import sqlite3
from application_components import *
import pandas as pd
import dash_dangerously_set_inner_html as ds
from datashop.datashop import df_scaler
from datashop.datashop import min_max_col
import dash_table
import dash_bootstrap_components as dbc

#july 22 test

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app=dash.Dash(__name__)
app.title = "Crude Oil Dashboard"



app.layout = html.Div([
    title_div,
    dcc.Tabs(
        id='main_tabs',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        value='main',
        children=[
            dcc.Tab(
                label='Main',
                value='main',
                style=tab_style,
                selected_style=sel_tab
                ),
            dcc.Tab(
                label='News',
                value='report',
                style=tab_style,
                selected_style=sel_tab
                ),
            dcc.Tab(
                label='Chart',
                value='chart',
                style=tab_style,
                selected_style=sel_tab
                ),
            dcc.Tab(
                label='Modeling',
                value='Modeling',
                style=tab_style,
                selected_style=sel_tab
                )
        ]
        ),
    html.Div(id='tabs-content')
], id='main_div')

@app.callback(Output('tabs-content','children'),
            [Input('main_tabs','value')])

def render_content(tab):
    if tab == 'main':
      
        return welcome_tab
    
    elif tab == 'report':
        return report

    elif tab == 'chart':

        return chart
    
    


@app.callback (Output(component_id='main-graph',component_property='figure'),
                [Input(component_id='generate',component_property='n_clicks')],
                [State(component_id='date_div',component_property='start_date'),
                State(component_id='date_div',component_property='end_date'),
                State(component_id='series_div',component_property='value')])

def update_value(n_clicks,start_date,end_date,series):      
    
    chart_data= []

    params = (start_date,end_date,)

    for ser in series:

        if ser == 'News':

            query2 = '''
            SELECT * FROM news WHERE news.Date > ? AND news.Date < ?
            '''

            
            conn = sqlite3.connect('data/energydash.db')
            df_news = pd.read_sql_query(query2,con=conn,params=params)
            df_news['y_val'] = min_max_col(df_news['DailyPrice']).add(0.1)
            conn.close()

            trace = go.Scatter(
                        x = df_news['Date'],
                        y =  df_news['y_val'],
                        text=df_news['main_headline'],
                        customdata=df_news['url'],
                        mode='markers',
                        hovertext=df_news['abstract'],
                        hoverinfo='text',
                        hovertemplate= news_hover,
                        marker_symbol='diamond-tall',
                        marker=dict(color=' #cecccc'),
                        name='News'
            )
        

        else:
            queries ={
                'DailyPrice':'SELECT Date, DailyPrice FROM DailyPrice',
                'WeeklyStocks':'SELECT Date, WeeklyStocks FROM WeeklyStocks',
                'ProductSupplied':'SELECT Date, ProductSupplied FROM ProductSupplied',
                'DIA_closing':'SELECT Date, DIA_closing FROM DIA'

            }
            
            
            query = queries[ser]
            conn = sqlite3.connect('data/energydash.db')
            df = pd.read_sql(query,conn)
            conn.close()
            
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date',inplace=True, drop=True)
            df.sort_index(inplace= True)
            df = df[start_date:end_date]
            df[ser] = min_max_col(df[ser])

            trace = go.Scatter(
            x = df[ser].index,
            y = df[ser],
            mode='lines',
            name=ser,
            line_color = line_colors[ser]
            )

        chart_data.append(trace)

    fig = go.Figure(data=chart_data,layout = layout)

    return fig

server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)

    print ('running')

    