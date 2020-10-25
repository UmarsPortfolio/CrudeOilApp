import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
from datetime import datetime as dt
import plotly
import plotly.graph_objs as go
import cufflinks as cf
import sqlite3
from appplication_components import *
import pandas as pd
import dash_dangerously_set_inner_html as ds
from datashop.datashop import df_scaler
from datashop.datashop import min_max_col

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
                label='Report',
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
                label='Map',
                value='map',
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
        return html.Iframe(srcDoc='/tab_main.html')

    elif tab == 'chart':

        return chart

@app.callback (Output(component_id='main-graph',component_property='figure'),
                [Input(component_id='generate',component_property='n_clicks')],
                [State(component_id='date_div',component_property='start_date'),
                State(component_id='date_div',component_property='end_date'),
                State(component_id='series_div',component_property='value')])

def update_value(n_clicks,start_date,end_date,series):      
    
    conn = sqlite3.connect('data/energydash.db')
    c = conn.cursor()

    query = '''
        SELECT * FROM original WHERE original.Date > ? AND original.Date < ?
     '''

    params = (start_date,end_date,)

    df = pd.read_sql_query(query,con=conn,params=params,index_col = 'Date')
    df = df_scaler(df,list(df.columns))

    chart_data= []

    for ser in series:

        if ser == 'News':

            query2 = '''
            SELECT * FROM news_merged WHERE news_merged.date_col > ? AND news_merged.date_col < ?
            '''

            params2 = (start_date,end_date,)

            df_news = pd.read_sql_query(query2,con=conn,params=params2)
            df_news['y_val'] = min_max_col(df_news['Daily_Price']).add(0.1)

            trace = go.Scatter(
            x = df_news['date_col'],
            y =  df_news['y_val'],
            text=df_news['main_headline'],
            customdata=df_news['url'],
            mode='markers',
            hovertext=df_news['abstract'],
            hoverinfo='text',
            hovertemplate= news_hover,
            marker_symbol='diamond-tall',
            marker=dict(color=' #cecccc')
            )
        

        else:
            ser = ser.replace(' ','_')
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

if __name__ == '__main__':
    app.run_server(debug=True)

    print ('running')

    