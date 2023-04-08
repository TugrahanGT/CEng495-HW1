from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)
client = MongoClient("mongodb+srv://tugrahangt:ZwW11yGKKlPJPJEE@clusterdb.9sbkfgg.mongodb.net/?retryWrites=true&w=majority")
db = client.hw1_mongoDB

users = db.users
categories = db.categories
categoriesList = list(categories.find())

clothings = categoriesList[0]
computerComponents = categoriesList[0]
monitors = categoriesList[0]
snacks = categoriesList[0]

clothingProducts = []
computerComponentProducts = []
monitorProducts = []
snackProducts = []

for item in clothings["items"]:
    clothingProducts.append(item)

for item in computerComponents["items"]:
    computerComponentProducts.append(item)

for item in monitors["items"]:
    monitorProducts.append(item)

for item in snacks["items"]:
    snackProducts.append(item)

print(clothingProducts[0])

@app.route("/")
def index():
    print(clothingProducts)
    return render_template("index.html", clothings = clothingProducts, computerComponents = computerComponentProducts,
                           monitors = monitorProducts, snacks = snackProducts)