from flask import Flask, render_template, request, url_for, redirect, flash
from pymongo import MongoClient
from bson.json_util import dumps
import os

secret_key = os.urandom(24).hex()

app = Flask(__name__)
app.config["SECRET_KEY"] = secret_key

clothingProducts = []
computerComponentProducts = []
monitorProducts = []
snackProducts = []

categories = None
users = None

client = MongoClient("mongodb+srv://tugrahangt:ZwW11yGKKlPJPJEE@clusterdb.9sbkfgg.mongodb.net/?retryWrites=true&w=majority")
db = client.hw1_mongoDB
users = db.users
categories = db.categories
categoriesList = list(categories.find())
clothings = categoriesList[0]
computerComponents = categoriesList[1]
monitors = categoriesList[2]
snacks = categoriesList[3]
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
    global user_loggedIn, snackProducts, computerComponentProducts, clothingProducts, monitorProducts, categories, users

    return render_template("index.html", clothings = clothingProducts, computerComponents = computerComponentProducts,
                           monitors = monitorProducts, snacks = snackProducts, user = user_loggedIn)

@app.route("/login/", methods = ("GET", "POST"))
def login():
    global user_loggedIn, users, clothingProducts, computerComponentProducts, snackProducts, monitorProducts
    if user_loggedIn["loggedIn"]:
        return redirect(url_for("index", clothings = clothingProducts, computerComponents = computerComponentProducts,
                        monitors = monitorProducts, snacks = snackProducts, user = user_loggedIn))
    else:
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
                    return redirect(url_for("index", clothings = clothingProducts, computerComponents = computerComponentProducts,
                            monitors = monitorProducts, snacks = snackProducts, user = user_loggedIn))
        return render_template("login.html")

@app.route("/logout", methods = ("GET", "POST"))
def logout():
    global user_loggedIn, clothingProducts, computerComponentProducts, snackProducts, monitorProducts
    user_loggedIn["loggedIn"] = False
    user_loggedIn["username"] = ""
    user_loggedIn["role"] = ""
    return redirect(url_for("index", clothings = clothingProducts, computerComponents = computerComponentProducts,
                           monitors = monitorProducts, snacks = snackProducts, user = user_loggedIn))

@app.route("/product", methods = ("GET", "POST"))
def product():
    global user_loggedIn, clothingProducts, computerComponentProducts, snackProducts, monitorProducts
    if request.method == "POST":
        username = request.form["username"]
        productID = int(request.form["itemID"])
        categoryID = int(request.form["categoryID"])
        if request.form["submit_btn"] == "rev":
            reviewText = request.form["review"]
            if add_review(username, reviewText, productID, categoryID):
                categoriesList = list(categories.find())
                if categoryID == 0:
                    clothingProducts = []
                    clothings = categoriesList[0]
                    for item in clothings["items"]:
                        clothingProducts.append(item)
                    return render_template("product.html", user = user_loggedIn, item = clothingProducts[productID], categoryID = categoryID)
                elif categoryID == 1:
                    computerComponentProducts = []
                    computerComponents = categoriesList[1]
                    for item in computerComponents["items"]:
                        computerComponentProducts.append(item)
                    return render_template("product.html", user = user_loggedIn, item = computerComponentProducts[productID], categoryID = categoryID)
                elif categoryID == 2:
                    monitorProducts = []
                    monitors = categoriesList[2]
                    for item in monitors["items"]:
                        monitorProducts.append(item)
                    return render_template("product.html", user = user_loggedIn, item = monitorProducts[productID], categoryID = categoryID)
                else:
                    snackProducts = []
                    snacks = categoriesList[3]
                    for item in snacks["items"]:
                        snackProducts.append(item)
                    return render_template("product.html", user = user_loggedIn, item = snackProducts[productID], categoryID = categoryID)
            else:
                print("here")
                rating = int(request.form["rating"])
                print("here")
                if add_rating(username, rating, productID, categoryID):
                    categoriesList = list(categories.find())
                    if categoryID == 0:
                        clothingProducts = []
                        clothings = categoriesList[0]
                        for item in clothings["items"]:
                            clothingProducts.append(item)
                        return render_template("product.html", user = user_loggedIn, item = clothingProducts[productID], categoryID = categoryID)
                    elif categoryID == 1:
                        computerComponentProducts = []
                        computerComponents = categoriesList[1]
                        for item in computerComponents["items"]:
                            computerComponentProducts.append(item)
                        return render_template("product.html", user = user_loggedIn, item = computerComponentProducts[productID], categoryID = categoryID)
                    elif categoryID == 2:
                        monitorProducts = []
                        monitors = categoriesList[2]
                        for item in monitors["items"]:
                            monitorProducts.append(item)
                        return render_template("product.html", user = user_loggedIn, item = monitorProducts[productID], categoryID = categoryID)
                    else:
                        snackProducts = []
                        snacks = categoriesList[3]
                        for item in snacks["items"]:
                            snackProducts.append(item)
                        return render_template("product.html", user = user_loggedIn, item = snackProducts[productID], categoryID = categoryID)
    itemID = int(request.args.get("product"))
    categoryID = int(request.args.get("categoryID"))
    if categoryID == 0:
        return render_template("product.html", user = user_loggedIn, item = clothingProducts[itemID], categoryID = categoryID)
    elif categoryID == 1:
        return render_template("product.html", user = user_loggedIn, item = computerComponentProducts[itemID], categoryID = categoryID)
    elif categoryID == 2:        
        return render_template("product.html", user = user_loggedIn, item = monitorProducts[itemID], categoryID = categoryID)
    else:
        return render_template("product.html", user = user_loggedIn, item = snackProducts[itemID], categoryID = categoryID)

def add_review(username, reviewText, productID, categoryID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    if categoryID == 0:
        return add_rev_clothing(username, reviewText, productID)
    elif categoryID == 1:
        return add_rev_compCom(username, reviewText, productID)
    elif categoryID == 2:
        return add_rev_mon(username, reviewText, productID)
    else:
        return add_rev_snack(username, reviewText, productID)
    
def add_rev_clothing(username, reviewText, productID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    reviewList = clothingProducts[productID]["reviews"]
    idx, flag = 0, False
    for review in reviewList:
        if review["author"] == username:
            flag = True
            break
        idx += 1
    if flag:
        clothingProducts[productID]["reviews"][idx]["reviewText"] = reviewText
        categories.update_one(
            {
                "_id": 0,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.reviews": clothingProducts[productID]["reviews"]
                }
            }
        )
    else:
        lastReviewID = reviewList[len(reviewList) - 1]["reviewID"]
        newReview = {"reviewID": lastReviewID + 1, "reviewText": reviewText, "author": username}
        reviewList.append(newReview)
        categories.update_one(
            {
                "_id": 0,
                "items.itemID": productID
            },
            {
                "$push": {
                    "items.$.reviews": newReview
                }
            }
        )
    return True

def add_rev_compCom(username, reviewText, productID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    reviewList = computerComponentProducts[productID]["reviews"]
    idx, flag = 0, False
    for review in reviewList:
        if review["author"] == username:
            flag = True
            break
        idx += 1
    if flag:
        computerComponentProducts[productID]["reviews"][idx]["reviewText"] = reviewText
        categories.update_one(
            {
                "_id": 1,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.reviews": computerComponentProducts[productID]["reviews"]
                }
            }
        )
    else:
        lastReviewID = reviewList[len(reviewList) - 1]["reviewID"]
        newReview = {"reviewID": lastReviewID + 1, "reviewText": reviewText, "author": username}
        reviewList.append(newReview)
        categories.update_one(
            {
                "_id": 1,
                "items.itemID": productID
            },
            {
                "$push": {
                    "items.$.reviews": newReview
                }
            }
        )
    return True

def add_rev_mon(username, reviewText, productID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    reviewList = monitorProducts[productID]["reviews"]
    idx, flag = 0, False
    for review in reviewList:
        if review["author"] == username:
            flag = True
            break
        idx += 1
    if flag:
        monitorProducts[productID]["reviews"][idx]["reviewText"] = reviewText
        categories.update_one(
            {
                "_id": 2,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.reviews": monitorProducts[productID]["reviews"]
                }
            }
        )
    else:
        lastReviewID = reviewList[len(reviewList) - 1]["reviewID"]
        newReview = {"reviewID": lastReviewID + 1, "reviewText": reviewText, "author": username}
        reviewList.append(newReview)
        categories.update_one(
            {
                "_id": 2,
                "items.itemID": productID
            },
            {
                "$push": {
                    "items.$.reviews": newReview
                }
            }
        )
    return True

def add_rev_snack(username, reviewText, productID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    reviewList = snackProducts[productID]["reviews"]
    idx, flag = 0, False
    for review in reviewList:
        if review["author"] == username:
            flag = True
            break
        idx += 1
    if flag:
        snackProducts[productID]["reviews"][idx]["reviewText"] = reviewText
        categories.update_one(
            {
                "_id": 3,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.reviews": snackProducts[productID]["reviews"]
                }
            }
        )
    else:
        lastReviewID = reviewList[len(reviewList) - 1]["reviewID"]
        newReview = {"reviewID": lastReviewID + 1, "reviewText": reviewText, "author": username}
        reviewList.append(newReview)
        categories.update_one(
            {
                "_id": 3,
                "items.itemID": productID
            },
            {
                "$push": {
                    "items.$.reviews": newReview
                }
            }
        )
    return True


def add_rating(username, rating, productID, categoryID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    if categoryID == 0:
        return add_rate_clothing(username, rating, productID)
    elif categoryID == 1:
        return add_rate_compCom(username, rating, productID)
    elif categoryID == 2:
        return add_rate_mon(username, rating, productID)
    else:
        return add_rate_snack(username, rating, productID)
    

def add_rate_clothing(username, rating, productID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    ratingList = clothingProducts[productID]["ratings"]
    idx, flag, totalRating = 0, False, 0
    for ratings in ratingList:
        if ratings["author"] == username:
            flag = True
            break
        idx += 1
    if flag:
        ratingList[idx]["rating"] = rating
        ratingCount = len(ratingList)
        for ratings in ratingList:
            totalRating += ratings["rating"]
        avgRating = totalRating / ratingCount
        categories.update_one(
            {
                "_id": 0,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.ratings": ratingList,
                    "items.$.rating": avgRating
                }
            }
        )
    else:
        lastRatingID = ratingList[len(ratingList) - 1]["ratingID"]
        ratingCount = len(ratingList)
        for ratings in ratingList:
            totalRating += ratings["rating"]
        avgRating = (totalRating + rating) / (ratingCount + 1)
        newRating = {"ratingID": lastRatingID + 1, "rating": rating, "author": username}
        categories.update_one(
            {
                "_id": 0,
                "items.itemID": productID
            },
            {
                "$push": {
                    "items.$.ratings": newRating
                },
                "$set": {
                    "items.$.rating": avgRating            
                }
            }
        )
    return True

def add_rate_compCom(username, rating, productID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    ratingList = computerComponentProducts[productID]["ratings"]
    idx, flag, totalRating = 0, False, 0
    for ratings in ratingList:
        if ratings["author"] == username:
            flag = True
            break
        idx += 1
    if flag:
        ratingList[idx]["rating"] = rating
        ratingCount = len(ratingList)
        for ratings in ratingList:
            totalRating += ratings["rating"]
        avgRating = totalRating / ratingCount
        categories.update_one(
            {
                "_id": 1,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.ratings": ratingList,
                    "items.$.rating": avgRating
                }
            }
        )
    else:
        lastRatingID = ratingList[len(ratingList) - 1]["ratingID"]
        ratingCount = len(ratingList)
        for ratings in ratingList:
            totalRating += ratings["rating"]
        avgRating = (totalRating + rating) / (ratingCount + 1)
        newRating = {"ratingID": lastRatingID + 1, "rating": rating, "author": username}
        categories.update_one(
            {
                "_id": 1,
                "items.itemID": productID
            },
            {
                "$push": {
                    "items.$.ratings": newRating
                },
                "$set": {
                    "items.$.rating": avgRating            
                }
            }
        )
    return True

def add_rate_mon(username, rating, productID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    ratingList = monitorProducts[productID]["ratings"]
    idx, flag, totalRating = 0, False, 0
    for ratings in ratingList:
        if ratings["author"] == username:
            flag = True
            break
        idx += 1
    if flag:
        ratingList[idx]["rating"] = rating
        ratingCount = len(ratingList)
        for ratings in ratingList:
            totalRating += ratings["rating"]
        avgRating = totalRating / ratingCount
        categories.update_one(
            {
                "_id": 2,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.ratings": ratingList,
                    "items.$.rating": avgRating
                }
            }
        )
    else:
        lastRatingID = ratingList[len(ratingList) - 1]["ratingID"]
        ratingCount = len(ratingList)
        for ratings in ratingList:
            totalRating += ratings["rating"]
        avgRating = (totalRating + rating) / (ratingCount + 1)
        newRating = {"ratingID": lastRatingID + 1, "rating": rating, "author": username}
        categories.update_one(
            {
                "_id": 2,
                "items.itemID": productID
            },
            {
                "$push": {
                    "items.$.ratings": newRating
                },
                "$set": {
                    "items.$.rating": avgRating            
                }
            }
        )
    return True

def add_rate_snack(username, rating, productID):
    global clothingProducts, computerComponentProducts, snackProducts, monitorProducts, categories
    ratingList = snackProducts[productID]["ratings"]
    idx, flag, totalRating = 0, False, 0
    for ratings in ratingList:
        if ratings["author"] == username:
            flag = True
            break
        idx += 1
    if flag:
        ratingList[idx]["rating"] = rating
        ratingCount = len(ratingList)
        for ratings in ratingList:
            totalRating += ratings["rating"]
        avgRating = totalRating / ratingCount
        categories.update_one(
            {
                "_id": 3,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.ratings": ratingList,
                    "items.$.rating": avgRating
                }
            }
        )
    else:
        lastRatingID = ratingList[len(ratingList) - 1]["ratingID"]
        ratingCount = len(ratingList)
        for ratings in ratingList:
            totalRating += ratings["rating"]
        avgRating = (totalRating + rating) / (ratingCount + 1)
        newRating = {"ratingID": lastRatingID + 1, "rating": rating, "author": username}
        categories.update_one(
            {
                "_id": 3,
                "items.itemID": productID
            },
            {
                "$push": {
                    "items.$.ratings": newRating
                },
                "$set": {
                    "items.$.rating": avgRating            
                }
            }
        )
    return True