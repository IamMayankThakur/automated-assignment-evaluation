from pymongo import MongoClient
import pandas as pd
client = MongoClient("mongodb://localhost:27017/")
db=client.A1

def insertCSV():
    AreaNameEnum = db.areaName
    df = pd.read_csv("AreaNameEnum.csv") 
    records_ = df.to_dict(orient = 'records')
    AreaNameEnum.insert_many(records_ )

insertCSV()
