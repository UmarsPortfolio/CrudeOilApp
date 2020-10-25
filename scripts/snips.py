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
