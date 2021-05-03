import requests
from flask_pymongo import MongoClient
from flask import jsonify


cluster = MongoClient('mongodb+srv://admin:5zr5FSiR5rS4e2sH@cluster0.hjoot.mongodb.net/maindb?retryWrites=true&w=majority')
db = cluster['maindb']
col = db['person']
results = col.find({})
print(list(results))
