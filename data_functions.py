from pprint import pprint as pp
import requests
import pandas as pd
import json
import math
import datetime as dt
import sqlite3
import time 
import os
import dash_html_components as html
from datashop import *
import datetime as dt

import os
from pathlib import Path

working_dir = str(Path(os.path.dirname(os.path.realpath(__file__))))

#from common import working_dir
#working_dir = str(working_dir) + '/'

with open (working_dir + '/data/cache.json','r') as cache_file:
    cache_dict = json.load(cache_file)

with open (working_dir + '/data/api_keys.json','r') as cache_file:
    api_keys = json.load(cache_file)

#path = 'c:/prompt_root/CrudeOilApp'
path = '/home/khan/CrudeOilApp'
relpath = '/data/nyt_jsons/'

    

################# FUNCTIONS

def extractRow(row):
    list = row['keywords']
    all_keywords = ''
    for num,item in enumerate(list):
        row[str(num).zfill(2) + '_type'] = item['name']
        row[str(num).zfill(2) + '_keyword'] = item['value']
        all_keywords = all_keywords + '; ' + str(item['value'])

    row['all_keywords'] = all_keywords
    return row

def makelink(url):
    link = html.A(html.P('Full Article'),href=url)
    return link
################### Classes


###____________     Energy Information Agency 

class EIA_Series:
    
    eia_api_url= 'http://api.eia.gov/series/?api_key={}&series_id='.format(api_keys['eia'])
    
    
    def __init__(
        self,
        id,
        name = None,
        start = '20010101',
        end = None,
        desc = None,
        date_format='%Y%m%d',
        scale = False
    ):
        
        if name == None:
            self.name = id
        else:
            self.name = name
    
        self.desc = desc
        self.scale = scale
        self.date_format = date_format
        self.end = end
        self.query = self.eia_api_url + id+'&start=' + start 

        if self.end != None:
            self.query = self.query + '&end=' + self.end           
        
        self.request = requests.get(self.query)
        self.series_dict = json.loads(self.request.text)
        self.make_df()
        

    def __getitem__(self,sliced):
        return self.frame[sliced]
        
    def show_response(self):
        
        pp.pprint(self.series_dict)
          
        
    def make_df(self,data_col='data',date_col='Date'):
        
        #_______     Slice out JSON to get series
        self.data_col = data_col
        self.date_col = date_col
        
        self.series_list=self.series_dict['series'][0][data_col]
        
        #________        Put it into frame
        self.frame = pd.DataFrame(self.series_list)
        self.frame.columns=[date_col, self.name]     
        
        #______      Convert to datetime and set index
        
    
        self.frame[self.date_col]=pd.to_datetime(
            self.frame[self.date_col],
            format = self.date_format
        )
        
        self.frame.set_index(
            self.date_col,drop=True,inplace=True)        
        self.frame.sort_index(ascending=True,inplace=True)  
        self.frame = self.frame.asfreq(freq='D').fillna(method='ffill')

        self.frame['date_only'] = self.frame.index.astype('str').str.slice(stop=10)
   

        #______   caputure data as series for convenience attribute

        self.series = self.frame.iloc[:,0]    
        
        if self.scale == True:
            self.scaler()
        
    def scaler(self):

        self.frame['scaled_'+self.name] = min_max_col(self.series)
        self.scaled = self.frame['scaled_'+self.name]



    def chart(self):
        self.fig,self.ax = plt.subplots(figsize=(10,6))
        self.ax.plot(self.frame)
    def report(self):
        print(
        "Earliest Point: {} \n".format(self.data.iloc[0].name),
        "Latest Point: {} \n".format(self.data.iloc[-1].name),
        ""
        )

class Depot:

    def __init__(self):

        self.features = {} 

    def ingest(self,feature):

        self.feature = feature

        if len(self.features) == 0:
            self.originals = self.feature.frame[self.feature.name]
            self.scaled = self.feature.frame['scaled_'+self.feature.name]
  

        else:
            self.originals = pd.merge_asof(
                self.originals,
                self.feature.frame[self.feature.name],
                right_index=True,
                left_index=True
                )

            self.scaled = pd.merge_asof(
                self.scaled,
                self.feature.frame['scaled_'+ self.feature.name],
                right_index=True,
                left_index=True
                )


        self.features[self.feature.name] = self.feature




###_____________   New York Times API

class nytResp():
    def __init__(self,start_date,end_date,query_term):
        self.start_date = start_date
        self.end_date = end_date
        self.query_term = query_term
        self.key = api_keys['nyt']
        self.target_url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?api-key={}'.format(self.key)
        self.cache_dict = {}
        self.cache_dict['news_update'] = str(dt.datetime.now())
        self.get_meta()


    def get_meta(self):

        self.params ={
        'begin_date':self.start_date,
        'end_date':self.end_date,
        'q':self.query_term,
        }

        self.first_response_raw = requests.get(self.target_url,self.params)
        self.first_response = json.loads(self.first_response_raw.text)

        self.response_meta = self.first_response['response']['meta']

        self.total_pages = math.ceil(self.response_meta['hits']/10)
        self.hits = self.response_meta['hits']

       
        self.cache_dict['hits'] = self.hits
        self.cache_dict['total_pages'] = self.total_pages

        if self.hits > 0:
            self.get_docs()

    def get_docs(self):

        self.doc_collection = []

        for page in range(0,self.total_pages):

            self.params['page']= page

            self.last_response_raw = requests.get(self.target_url,self.params)
            self.last_response = json.loads(self.last_response_raw.text)

            self.last_docs = self.last_response['response']['docs']

            for doc in self.last_docs:
                self.doc_collection.append(doc)

            if self.total_pages > 1:
                time.sleep(7)

        self.build_dataframe()

    def build_dataframe(self):

        self.frame_list = []

        for doc in self.doc_collection:
            self.doc_dict = {
                'id':doc['_id'],
                'Date':doc['pub_date'][:19].replace("T", " "),
                'date_only': doc['pub_date'][:10],
                'abstract':doc['abstract'],
                'doc_type':doc['document_type'],
                'main_headline':doc['headline']['main'],
                'keywords':doc['keywords'],
                'newsdesk':doc['news_desk'],
                'url':doc['web_url'],
                'retrieved':str(dt.datetime.now())             
                
            }

            self.frame_list.append(self.doc_dict)
        
        self.frame = pd.DataFrame(self.frame_list)
        #self.frame = self.frame.apply(extractRow,axis=1)
        self.frame['keywords'] = self.frame['keywords'].astype(str)

    


def jsons_to_frame(abs_path,rel_path,conn):
    art_list = []

    for file in os.listdir(working_dir + rel_path):
        with open(working_dir + rel_path + file) as json_file:
            chunk = json.load(json_file)
            for doc in chunk:
                doc_dict = {
                        'id':doc['_id'],
                        'Date':doc['pub_date'][:19].replace("T", " "),
                        'date_only': doc['pub_date'][:10],
                        'abstract':doc['abstract'],
                        'doc_type':doc['document_type'],
                        'main_headline':doc['headline']['main'],
                        'keywords':doc['keywords'],
                        'newsdesk':doc['news_desk'],
                        'url':doc['web_url'],
                        'retrieved':str(dt.datetime.now())                
                        
                    }
                art_list.append(doc_dict)

    frame = pd.DataFrame(art_list)
    #frame = frame.apply(extractRow,axis=1)
    frame['keywords'] = frame['keywords'].astype(str)

    frame.to_sql('news',conn, if_exists='replace')

    return frame

            
