from flask import Flask
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)
client = MongoClient("mongodb+srv://tugrahangt:ZwW11yGKKlPJPJEE@clusterdb.9sbkfgg.mongodb.net/?retryWrites=true&w=majority")
db = client.hw1_mongoDB

users = db.users
categories = db.categories

categoriesList = list(categories.find())
categoryNames = list()
for category in categoriesList:
    categoryNames.append(category["name"])
print(categoryNames)

@app.route("/")
def hello():
    return "Hello, World! " + str(categoryNames[0])