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

user_loggedIn = {"loggedIn": False, "username": "", "role": ""}

@app.route("/")
def index():
    global user_loggedIn
    print(clothingProducts)
    return render_template("index.html", clothings = clothingProducts, computerComponents = computerComponentProducts,
                           monitors = monitorProducts, snacks = snackProducts, user = user_loggedIn)

@app.route("/login/", methods = ("GET", "POST"))
def login():
    global user_loggedIn
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(username, password)
        if not username:
            flash("Please enter a username!")
        elif not password:
            flash("Please enter a password!")
        else:
            result = list(users.find({"username": username}))[0]
            if not result:
                flash("Wrong password or username")
            elif password != result["password"]:
                flash("Wrong password or username")
            else:
                user_loggedIn["loggedIn"] = True
                user_loggedIn["username"] = username
                user_loggedIn["role"] = result["role"]["type"]
                print(user_loggedIn)
                return redirect(url_for("index", clothings = clothingProducts, computerComponents = computerComponentProducts,
                           monitors = monitorProducts, snacks = snackProducts, user = user_loggedIn))
    return render_template("login.html")

@app.route("/product", methods = ("GET", "POST"))
def product():
    if request.method == "POST":
        username = request.form["username"]
        reviewText = request.form["review"]
        productID = request.form["itemID"]
        categoryID = request.form["categoryID"]
        print(username, reviewText, productID, categoryID)
    itemID = int(request.args.get("product"))
    categoryID = int(request.args.get("categoryID"))
    if categoryID == 0:
        return render_template("product.html", user = user_loggedIn, item = clothingProducts[itemID], categoryID = categoryID)
    else:
        return render_template("product.html", user = user_loggedIn, item = snackProducts[itemID], categoryID = categoryID)
