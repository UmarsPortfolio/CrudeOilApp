from pprint import pprint as pp
import requests
import pandas as pd
import json



import json

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

        for doc in docs:
            collection.append(doc)

        time.sleep(7)

    with open('nyt_jsons/' + str(start_date) + '_articles.json', 'w') as f:
        json.dump(collection, f)   


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
            'keywords':doc['keywords'],
            'newsdesk':doc['news_desk'],
            'url':doc['web_url']
            
            

        }

        doc_list.append(doc_dict)

    frame = pd.DataFrame(doc_list)
    return frame  
