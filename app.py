from flask import Flask, render_template, request, url_for, redirect, flash
from pymongo import MongoClient
from bson.json_util import dumps
import os

secret_key = os.urandom(24).hex()

app = Flask(__name__)
app.config["SECRET_KEY"] = secret_key
client = MongoClient("mongodb+srv://tugrahangt:ZwW11yGKKlPJPJEE@clusterdb.9sbkfgg.mongodb.net/?retryWrites=true&w=majority")
db = client.hw1_mongoDB

users = db.users

print(list(users.find({"username": "asd"})))

categories = db.categories
categoriesList = list(categories.find())

clothings = categoriesList[0]
computerComponents = categoriesList[1]
monitors = categoriesList[2]
snacks = categoriesList[3]

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


@app.route("/")
def index():
    print(clothingProducts)
    return render_template("index.html", clothings = clothingProducts, computerComponents = computerComponentProducts,
                           monitors = monitorProducts, snacks = snackProducts)

@app.route("/login/", methods = ("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(username, password)
        if not username:
            flash("Please enter a username!")
        elif not password:
            flash("Please enter a password!")
        else:
            result = list(users.find({"username": username}))
            if not result:
                flash("Wrong password or username")
            elif password != result["password"]:
                flash("Wrong password or username")
            else:
                return redirect(url_for("index"))
    return render_template("login.html")