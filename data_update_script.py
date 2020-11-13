from data_functions import *
import math
import datetime as dt
import sqlite3
import pandas as pd
import time
from common import working_dir
#while True:

    #time.sleep(900)

    #path = 'c:/prompt_root/CrudeOilApp'
    #relpath = '/data/nyt_api/nyt_jsons/'

working_dir = str(working_dir)

conn = sqlite3.connect(working_dir + '/data/energydash.db')



log_dict = {}

#______________________             Update EIA data
eia_dict = {
    'PET.WTTSTUS1.W':['WeeklyStocks','235081','%Y%m%d'],
    'PET.RWTC.D':['DailyPrice','241335','%Y%m%d'],
    'PET.WRPUPUS2.W':['ProductSupplied','401676','%Y%m%d']
}

with open (working_dir + '/' + 'data/dummy_cache.json','r') as cache_file:
#with open (working_dir + '/' + 'data/cache.json','r') as cache_file:
    cache_dict = json.load(cache_file)

with open (working_dir + '/' + 'data/daily_log.json','r') as cache_file:
    log_dict = json.load(cache_file)

#_________ Base URL. Requires category ID to return series in that category"

eia_api_url= 'http://api.eia.gov/updates/?api_key=651b30b69f4f47a13a2912d673f7da93&category_id='



# ________ Get last update time for each series. 

current_eia = {}

for key,val in eia_dict.items():

    #load last recorded update time from cache

    last_update = cache_dict[key]

    # Get update time from API

    url = eia_api_url + val[1] + '&rows=10000'
    request = requests.get(url)
    dict = json.loads(request.text)   

    for update in dict['updates']:
        if update['series_id'] == key:
            new_update = update['updated']

    #compare both, get updates if needed and add to table

    if new_update > last_update:

        # get last date in dataframe
        query = " SELECT MAX(Date) from {}".format(val[0])
        last_date = conn.execute(query).fetchall()[0][0]
        last_date_eia = dt.datetime.strptime(
            last_date[:10], '%Y-%m-%d').strftime(val[2])
        
        #get new data from EIA

        new_data = EIA_Series(
            key, 
            name=val[0],
            start = last_date_eia,
            date_format = val[2]).frame

        # filter to make sure last date isnt repeated
        new_data = new_data[new_data.index > pd.Timestamp(last_date)]
        

        # Add to log
        records = new_data.to_dict(orient='records')
        for record in records:
            log_dict[val[0]].append(record)

        #append to dataframe        
        new_data.to_sql(val[0],conn,if_exists='append')   

        # store new update list in cache dict for next round

        cache_dict[key] = new_update


##___________________________   Get DOW

url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=DIA&interval=15min&outputsize=full&apikey=' + key

request = requests.get(url)

req_dict = json.loads(request.text)

df = pd.DataFrame.from_dict(req_dict['Time Series (15min)'],orient = 'index')
df = df.rename(columns={'4. close':'DIA_closing'})
df['Date'] = df.index
df['DIA_closing'] = df['DIA_closing'].astype('float')
df['date_only'] = df['Date'].str.slice(stop=10)
df.set_index('Date',inplace=True)
df.index = pd.to_datetime(df.index)
df.sort_index(inplace=True)
df = df.rename(columns={'4. close':'DIA_closing'})

query = " SELECT MAX(Date) FROM DIA LIMIT 1"
last_dia_date = conn.execute(query).fetchall()[0][0]
df = df[df.index > last_dia_date][['date_only','DIA_closing']]

if len(df) > 0:
    records = df.to_dict(orient='records')
    for record in records:
        log_dict['Dow'].append(record)
df.to_sql('DIA',conn,if_exists='append')

#_________     Get most recent EIA and Dow values 

last_values = {}
for key,val in eia_dict.items():
    query = " SELECT * FROM {} ORDER BY date_only DESC LIMIT 1".format(val[0])
    df = pd.read_sql(query,conn)
    dict = df.to_dict(orient='list')
    last_values[val[0]] = dict[val[0]]

query = " SELECT * FROM DIA ORDER BY Date DESC LIMIT 1"
df = pd.read_sql(query,conn)
last_values['DIA_closing'] = df.iloc[0,2]

df_current = pd.DataFrame(last_values)

##__________________________________         Update news

query = " SELECT MAX(Date) FROM news LIMIT 1"
last_archive_date = str(conn.execute(query).fetchall()[0][0])

end_date = str(dtime.datetime.today().date())

query = 'Oil (Petroleum) and Gasoline'

recents_call = nytResp(last_archive_date,end_date,query)

if recents_call.hits > 0:

    df_hits = df_hits

    query_lastnews = " SELECT * FROM news ORDER BY Date DESC LIMIT 50"
    df_lastnews = pd.read_sql(query_lastnews,conn)
    df_lastnews = df_lastnews[['Date','abstract''id']]

    df_hits = df_hits[~df_hits['id'].isin(df_lastnews['id'])]
    
    
    hits = len(df_hits)   

    if hits > 0:               
        
        records = df_hits[['abstract','Date','url']].to_dict(orient='records')
        for record in records:
            log_dict['News'].append(record)

        df_hits.to_sql('news',conn,if_exists='append')

    #__________  record news updated time

cache_dict['news_update'] = end_date

with open (working_dir + '/' + 'data/cache.json','w') as cache_file:
    json.dump(cache_dict,cache_file)

with open (working_dir + '/' + 'data/daily_log.json','w') as cache_file:
    json.dump(log_dict,cache_file)

conn.commit()
conn.close()

print('Update ran on {}. No issues'.format(str(dt.datetime.now())))
