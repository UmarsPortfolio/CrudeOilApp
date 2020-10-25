import pandas as pd
import requests
import json
import functools
from sklearn import preprocessing
#import pyodbc
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
from datetime import datetime as dt
import plotly
import plotly.graph_objs as go
import cufflinks as cf
import sqlite3

#july 22 test

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

dash_app=dash.Dash(__name__)
app=dash_app.server
dash_app.title = "Crude Oil Dashboard"

checkoptions = [
    {'label':'Weekly Stocks','value':'Weekly Stocks'},
    {'label':'Spot Price', 'value':'Spot Price'},
    {'value':'Crude Supplied','label':'Crude Supplied'}
    ]


dash_app.layout = html.Div(children=[
            dcc.Checklist(id='maincheck',
            options=checkoptions,
            value=['Spot Price']
            ),
         dcc.DatePickerRange(
            id='my-date-picker-range',
            start_date=dt(2008, 1, 1),
            end_date= dt.now()
            ),    
        html.Button(
            'Rescale',
            id='scalebutton',
        ),
        html.Button(
            'Reset',
            id='reset'
        ), 
        html.Div(
            id='output',
            children=[
                dcc.Graph(
                    id='main-graph',
                    style={
                    'height': '100vh',
                    'backgroundColor':'black'
                    },
                    animate=True)
            ]
            ),
]
)



@dash_app.callback(
    Output(component_id='main-graph',component_property='figure'),
    [Input(component_id='maincheck',component_property='value'),
    Input(component_id='my-date-picker-range',component_property='start_date'),
    Input(component_id='my-date-picker-range',component_property='end_date')],
    )

def update_value(input_data,start_date,end_date):

       
    dtstart_date=dt.strptime(start_date[:10],'%Y-%m-%d')
    dtend_date= dt.strptime(end_date[:10],'%Y-%m-%d') # 

    sql_start = dtstart_date.isoformat(" ")
    sql_end = dtend_date.isoformat(" ")    

    conn = sqlite3.connect('oilstocks.db')
    c = conn.cursor()
    scaled_df=pd.read_sql_query('SELECT * FROM crudestocks ORDER BY "Date" ASC',conn,index_col="Date")    
    scaled_df=scaled_df[sql_start:sql_end]

    for col in scaled_df:
        scaled_df[col]=preprocessing.scale(scaled_df[col])

    chartdata=[]
    
    news_df=pd.read_sql_query('SELECT date, description,yvalue FROM newstable ORDER BY "date" ASC',conn,index_col="date")
    newschart=go.Scatter(x=news_df.index,y=news_df['yvalue'],hovertext=news_df['main_headline'],mode='markers')
    chartdata.append(newschart)

    
    for val in input_data:
        
        x = scaled_df.index
        y = scaled_df[val]
        
        chart = go.Scatter(x=x,y=y,name=val,mode='lines')
        chartdata.append(chart)

    layout=go.Layout(
        xaxis=dict(
            type='date',
            tickformat='%b-%d-%Y',
            zeroline=False,
            showgrid=False,
            range=[scaled_df.index.values[0],scaled_df.index.values[-1]],            
        ),
        yaxis=dict(
            zeroline=False,
            showgrid=False,
            showticklabels=False,           
            range=[scaled_df.values.min(),scaled_df.values.max()],
            
        ),
       # clickmode='event'
    )
    figure = {
            'data':chartdata,
            'layout':layout
        }
    
    return figure
        
@dash_app.callback(
    Output(component_id='my-date-picker-range',component_property='start_date'),
    [Input(component_id='scalebutton',component_property='n_clicks'),
    Input(component_id='reset',component_property='n_clicks')], 
    [State(component_id='main-graph',component_property='relayoutData')]  
    )
def updatestart(selectedData,reset,relayoutData):
    if relayoutData is not None and relayoutData.get('xaxis.range[0]') is not None : 
        return dt.strptime(relayoutData['xaxis.range[0]'][:10],'%Y-%m-%d')
    else:
        return '2008-01-01 00:00:00'

@dash_app.callback(
    Output(component_id='my-date-picker-range',component_property='end_date'),
    [Input(component_id='scalebutton',component_property='n_clicks'),
    Input(component_id='reset',component_property='n_clicks')],
    [State(component_id='main-graph',component_property='relayoutData')]
 )
def updateend(selectedData,reset,relayoutData):
    if relayoutData is not None and relayoutData.get('xaxis.range[1]') is not None:
        return dt.strptime(relayoutData['xaxis.range[1]'][:10],'%Y-%m-%d')
    else:
        return dt.now() 

if __name__ == '__main__':
    dash_app.run_server(debug=True)
 km/.,n=
    print ('running')

