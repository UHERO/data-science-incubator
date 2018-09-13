from pymongo import MongoClient
import os
import pandas as pd

uri = 'mongodb://' + os.environ['MONGO_URL']

client = MongoClient(uri, username=os.environ['MONGO_USER'], password=os.environ['MONGO_PASS'], authSource='admin')
db = client['HonoluluProperty']

cursor = db['permits'].find({})

permits = list(cursor)

df = pd.io.json.json_normalize(permits)

df.to_csv('currentPermits.csv')