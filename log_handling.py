import json
import datetime as dt

with open ('data/daily_log.json','r') as cache_file:
    daily_log = json.load(cache_file)

today = str(dt.date.today())

with open ('data/logs/{}_log.json'.format(today),'w') as cache_file:
    json.dump(daily_log,cache_file)

log = {}

eia_dict = {
    'PET.WTTSTUS1.W':['WeeklyStocks','235081','%Y%m%d'],
    'PET.RWTC.D':['DailyPrice','241335','%Y%m%d'],
    'PET.WRPUPUS2.W':['ProductSupplied','401676','%Y%m%d']
}

for val in eia_dict.values():
    log[val[0]] = []

log['Dow'] = []
log['News']= []

with open ('data/daily_log.json','w') as cache_file:
    json.dump(log,cache_file)

