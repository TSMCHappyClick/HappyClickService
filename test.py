
from flask import Flask
from flask_pymongo import PyMongo

PASSWORD = '123'
DATABASE = 'Cluster0'
CONNECTION_STRING = f"mongodb://danny:{PASSWORD}@cluster0-shard-00-00.wow4z.mongodb.net:27017,cluster0-shard-00-01.wow4z.mongodb.net:27017,cluster0-shard-00-02.wow4z.mongodb.net:27017/{DATABASE}?ssl=true&replicaSet=atlas-q4etkp-shard-0&authSource=admin&retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.test

def test():
    # db.db.collection.insert_one({"name": "John"})
    print( "Connected to the data base!" )

test()