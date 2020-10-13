import requests
import json
from datashop import * 
import time

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

start = 20000101
end = 20000601
collection = get_docs(start,end)
#fram = parse_docs(collection)
print(collection)
