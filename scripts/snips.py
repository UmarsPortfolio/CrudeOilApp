      self.cull_series = pd.Series()

        self.base = int(base_threshold * 100)
    
        for x in range (1,self.base,1):
            
            self.current = round(float(x/100),2)
            self.cull_outliers(threshold = self.current)
            self.cull_loss = (len(self.series) -len(self.culled))/len(self.series)
            self.cull_series[str(self.current)] = self.cull_loss
        
        self.cull_fig,self.cull_ax = plt.subplots(figsize=(16,6))
        self.cull_ax.bar(self.cull_series.index,self.cull_series)
        self.cull_ax.tick_params(
                    axis='x', 
                    labelrotation=55,
                    length=10,
                    labelsize= 10
                    )


                    ##################################################################
self.series_map = {
            self.feature.name:self.originals,
            'scaled':self.scaled,
            'delta':self.deltas,
            'rolling':self.rolling
        }    

        ##########################
         self.features[self.feature.name] = self.feature
        for col in self.feature.series_frame.columns:
            self.feat_type = col.split('_')[0]
            self.ingest_frame = self.series_map[self.feat_type]
            self.ingest_frame = pd.merge_asof(
                self.series_map[self.feat_type],
                self.feature.series_frame[col],
                right_index=True,
                left_index=True
                )


##################          NYT API

import requests
import json
from datashop import * 
import time
import math


key = 'm6HsQpjurALl27VpNGB1o4nAcr50o5wt'

response = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?api-key={}'.format(key)



def get_docs(start_date,end_date):

    params ={
        'begin_date':start_date,
        'end_date':end_date,
        'q':'Oil (Petroleum) and Gasoline',
    }
    request = requests.get(response,params)
    series_dict = json.loads(request.text)

    meta = series_dict['response']['meta']

    pages = math.ceil(meta['hits']/10)

    collection = []

    for page in range(0,pages):

        params['page']= page

        request = requests.get(response,params)
        series_dict = json.loads(request.text)

        docs = series_dict['response']['docs']

        collection.append(docs)

        time.sleep(7)
    
    return collection    

def parse_docs(docs):
    doc_list = []

    for doc in docs:
        doc_dict = {
            'id':doc['_id'],
            'date':doc['pub_date'],
            'abstract':doc['abstract'],
            'doc_type':doc['document_type'],
            'main_headline':doc['headline']['main'],
            'print_headline':doc['headline']['print_headline'],
            'keywords':doc['keywords']

        }

        doc_list.append(doc_dict)

    frame = pd.DataFrame(doc_list)
    return frame    

########## DASH DAT DIVS

html.Div(
            id='date_div',
            children=date_selector
        ),
        html.Div(
            id='series_div',
            children = [series_selector]
        ),
        html.Div(
            id='series_div',
            children = [series_selector]
        )


#______________

daily_price = EIA_Series('Daily Price','PET.RWTC.D')
dep.ingest(daily_price)

desc = ''
daily_production = EIA_Series('Weekly Stocks','PET.WTTSTUS1.W')
dep.ingest(daily_production)

desc = 'US imports of crude oil, monthly'

monthly_imports = EIA_Series('Monthly Imports','PET.MCRIMUS1.M',desc,date_format='%Y%m' )
dep.ingest(monthly_imports)



weekly_sales = EIA_Series('Product Sold','PET.WRPUPUS2.W')
dep.ingest(weekly_sales)

weekly_inventory = EIA_Series('Weekly Inventory','PET.WCRSTUS1.W')
monthly_rigcount = EIA_Series("Rig Count",'PET.E_ERTRRO_XR0_NUS_C.M')


conn = sqlite3.connect('data/energydash.db')
c = conn.cursor()

df = dep.originals['2000-01-01':]
df.columns = [x.replace(' ','_') for x in df.columns]
df.to_sql("original",conn,if_exists='replace')

series = ['PET.RWTC.D','PET.WTTSTUS1.W','PET.MCRIMUS1.M','PET.WRPUPUS2.W']
for enum,update in enumerate(dict['updates']):
    if update['series_id'] in series:
        print(enum, update)


import requests
import json

eia_api_url= 'http://api.eia.gov/updates/?api_key=651b30b69f4f47a13a2912d673f7da93&category_id=241335'


request = requests.get(eia_api_url)
dict = json.loads(request.text)


# All table names

res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
for name in res:
    print (name[0])
#delete_table = ['news_merged']
for name in delete_table:
    query = 'DROP table {}'.format(name)
    res = conn.execute(query)