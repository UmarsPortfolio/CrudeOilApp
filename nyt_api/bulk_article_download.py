import os
import json
from nyt_api import *
import pandas as pd

art_list = []

for file in os.listdir('c:/prompt_root/CrudeOilApp/nyt_api/nyt_jsons'):
    with open('nyt_api/nyt_jsons/' + file) as json_file:
        data = json.load(json_file)
        art_list =art_list + data

final_frame = parse_docs(art_list)
final_frame.to_csv('data/nyt_articles.csv')