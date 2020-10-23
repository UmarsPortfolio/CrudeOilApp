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
import dash_dangerously_set_inner_html as ds

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


if __name__ == '__main__':
    app.run_server(debug=True)

    print ('running')
