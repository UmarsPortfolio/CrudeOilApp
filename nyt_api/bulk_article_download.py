import os

art_list = []

for file in os.listdir('nyt_jsons'):
    with open('nyt_jsons/' + file) as json_file:
        data = json.load(json_file)
        art_list =art_list + data

final_frame = parse_docs(art_list)
final_frame.to_csv('data/nyt_articles.csv')