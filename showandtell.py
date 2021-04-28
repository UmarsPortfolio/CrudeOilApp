import dash
import dash_core_components as dcc
import dash_html_components as html

app=dash.Dash(__name__)
app.title = "Crude Oil Dashboard"

app.layout = html.Div(
    children = [
        html.Div(
            children = [dcc.Markdown(title)],
            id='title_div',
            ),
        dcc.Tabs(
            id='main_tabs',
            parent_className='custom-tabs',
            className='custom-tabs-container',
            value='main',
            children=[
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
                    )
            ]
            ),
        html.Div(id='tabs-content')
        ], 

        
    id='main_div')


@app.callback(Output('tabs-content','children'),
            [Input('main_tabs','value')])

def render_content(tab):
    if tab == 'main':
        welcome_tab = html.Div('Welcome to Dashboard', id = 'welc_span')
      
        return welcome_tab
    
    elif tab == 'report':

        with open ('data/cache.json','r') as cache_file:
            cache_dict = json.load(cache_file)

        conn = sqlite3.connect('data/energydash.db')

        news_update = cache_dict['news_update']

        query = 'SELECT date,main_headline,url FROM news ORDER BY date DESC LIMIT 10'

        df_news = pd.read_sql_query(query,conn)
        df_news.columns = ['Date','Headline','URL']

        def makelink(url):
            link = html.A(html.P('Full Article'),href=url,target = '_blank')
            return link
            
        df_news['Link']= df_news['URL'].apply(makelink)
        df_news.drop('URL',axis=1,inplace= True)

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
        
        return report

    elif tab == 'chart':
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
            'DIA_closing':'#FFFF00',
            'Predicted': '#FF0000'
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
                'gridwidth':0.01,
                'gridcolor':'#ebe8e8',
                'showgrid':False,
                'showspikes':True,
                'color':'#ebe8e8',
                'showline':False,               
            },
            yaxis = {
                'showgrid':False,
                'visible':False
            },
            plot_bgcolor = '#252526',
            paper_bgcolor = '#252526',
            autosize=True,
            hovermode = 'closest',
            legend = dict(
                orientation='h',
                x=0.5,
                y=1,
                font=dict(
                color='#ebe8e8'
                )
        ))

        fig = go.Figure(data=chart_data,layout = layout)

        checkoptions = [
            {'value':'News','label':'News'},
            {'label':'Daily Price', 'value':'DailyPrice'},
            {'label':'Weekly Stocks','value':'WeeklyStocks'},
            {'label':'Product Sold', 'value':'ProductSupplied'},
            {'label':'DOW Jones','value':'DIA_closing'},
            {'label':'Predicted','value':'Predicted'}
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


        return chart
    
    elif tab == 'Modeling':
        ds_html = html.Img(src=app.get_asset_url('modeling.png'))

        return ds_html