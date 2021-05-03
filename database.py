from flask_pymongo import MongoClient

cluster = MongoClient(
    'mongodb+srv://admin:5zr5FSiR5rS4e2sH@cluster0.hjoot.mongodb.net/maindb?retryWrites=true&w=majority')