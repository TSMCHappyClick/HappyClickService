from flask_pymongo import pymongo
from pymongo import message

def connection():
    PASSWORD = '123'
    DATABASE = 'Cluster0'
    CONNECTION_STRING = f"mongodb://danny:{PASSWORD}@cluster0-shard-00-00.wow4z.mongodb.net:27017,cluster0-shard-00-01.wow4z.mongodb.net:27017,cluster0-shard-00-02.wow4z.mongodb.net:27017/{DATABASE}?ssl=true&replicaSet=atlas-q4etkp-shard-0&authSource=admin&retryWrites=true&w=majority"
    client = pymongo.MongoClient(CONNECTION_STRING)
    db = client

    return db

def get_divisions():
    divisions = ['台積總部及晶圓十二A廠','研發中心及晶圓十二B廠','晶圓十四A廠','晶圓十四B廠','晶圓十五A廠','晶圓十五B廠','台積電(南京)有限公司及晶圓十六廠'
,'晶圓十八廠'
,'晶圓三廠'
,'晶圓五廠'
,'晶圓六廠'
,'晶圓八廠'
,'台積電(中國)有限公司及晶圓十廠'
,'WaferTech L.L.C. 及晶圓十一廠'
,'SSMC (TSMC-NXP JV)'
,'晶圓二廠'
,'先進封測一廠'
,'先進封測二廠'
,'先進封測三廠'
,'先進封測五廠']
    return divisions



meds = [111426, 120649, 120000]