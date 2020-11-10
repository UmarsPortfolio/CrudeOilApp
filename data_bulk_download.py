from data_functions import *
import math
import datetime as dt
import sqlite3
import pandas as pd
from datashop import *
import datetime as dt

conn = sqlite3.connect('data/energydash.db')


with open ('data/api_keys.json','r') as cache_file:
    api_keys = json.load(cache_file)

##################  _____________________________________           EIA Build

start_date = '20010101'
#end_date = dt.date.today().strftime('%Y%m%d')
end_date = '20201026'           #dummy date - for testing updates
last_dow_date = str(dt.datetime.now() - dt.timedelta(10))[:10]

eia_dict = {
    'PET.WTTSTUS1.W':['WeeklyStocks','235081',start_date,'%Y%m%d'],
    'PET.RWTC.D':['DailyPrice','241335',start_date,'%Y%m%d'],
    'PET.WRPUPUS2.W':['ProductSupplied','401676',start_date,'%Y%m%d']
}

for key,val in eia_dict.items():

    #_____________ Get series from API

    e_ser = EIA_Series(
        key,name = val[0],
        date_format = val[3], 
        end = end_date)   

    #_____________ Send to SQL

    e_ser.frame.to_sql(val[0],conn,if_exists='replace')  

################## _______________________________________    Dow Jones

dow_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=DIA&outputsize=full&apikey=' + api_keys['alpha']

request = requests.get(dow_url)

req_dict = json.loads(request.text)

df = pd.DataFrame.from_dict(req_dict['Time Series (Daily)'],orient = 'index')
df = df.rename(columns={'4. close':'DIA_closing'})
df['Date'] = df.index
df['DIA_closing'] = df['DIA_closing'].astype('float')
df['date_only'] = df['Date']
df['Date'] = df['Date'].apply(lambda x: x + ' 16:00:00')
df.set_index('Date',inplace=True)
df.sort_index()
df = df[df.index < last_dow_date]
df[['date_only','DIA_closing']].to_sql('DIA',conn,if_exists='replace')

##################  _____________________________________           New York Times build

#_______________         Get latest articles 

last_archive_date = "2020-10-10T10:00:00"	
end_date = "2020-10-26T16:00:00"        # Testing
#end_date = str(dt.datetime.now())

query = 'Oil (Petroleum) and Gasoline'

recents_call = nytResp(last_archive_date,end_date,query)

with open ('data/nyt_jsons/recent.json','w') as new_file:
    json.dump(recents_call.doc_collection,new_file)
    
#_______________         Create df from JSON


frame = jsons_to_frame(path,relpath,conn)

#_______________         Load news into DF

query1 = 'SELECT * FROM news'
df_news=pd.read_sql(query1,conn)

#_______________         Load EIA into DFs

eia_frame = []

for key,val in eia_dict.items():
    query = 'SELECT * FROM {}'.format(val[0])
    df=pd.read_sql(query,conn)
    df.drop('Date',axis=1,inplace=True)
    eia_frame.append(df)

#_______________         Load Dow into DFs

query = 'SELECT date_only,DIA_closing FROM DIA'
df_dia=pd.read_sql(query,conn)
eia_frame.append(df_dia)


#_______________         Merge EIA frames with News

for frame in eia_frame:
    df_news = df_news.merge(
        frame,
        how='left',
        on='date_only'
    )


#_______________        Sort news and filter 

df_news.sort_values(by='date_only',inplace=True)
df_news = df_news[df_news['date_only'] > '2001-01-25']

#_______________        Forward fill empty rows

eia_cols = [val[0] for val in eia_dict.values()]
eia_cols.append('DIA_closing')
for col in eia_cols: 
    df_news[col].fillna(method='ffill',inplace=True)

# Replace SQL Table

df_news.to_sql('news',conn, if_exists='replace')


conn.commit()
conn.close()