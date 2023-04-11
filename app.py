from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_session import Session
from pymongo import MongoClient
from bson.json_util import dumps
import os

secret_key = os.urandom(24).hex()

app = Flask(__name__)
app.config["SECRET_KEY"] = secret_key
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

clothingProducts = []
computerComponentProducts = []
monitorProducts = []
snackProducts = []

categories = None
users = None

client = MongoClient("mongodb+srv://tugrahangt:ZwW11yGKKlPJPJEE@clusterdb.9sbkfgg.mongodb.net/?retryWrites=true&w=majority")
db = client.hw1_mongoDB
users = db.users
categories = db.finalizedCategories
categoriesList = list(categories.find())

clothings = categoriesList[0]
computerComponents = categoriesList[1]
monitors = categoriesList[2]
snacks = categoriesList[3]

categoriesList.clear()
all_items = {0: [], 1: [], 2: [], 3: []}

for item in clothings["items"]:
    all_items[0].append(item)
for item in computerComponents["items"]:
    all_items[1].append(item)
for item in monitors["items"]:
    all_items[2].append(item)
for item in snacks["items"]:
    all_items[3].append(item)


@app.route("/")
def index():
    global all_items
    if not request.args.get("categoryID"):
        return render_template("index.html", items = all_items, categoryID = -1)
    else:
        return render_template("index.html", items = all_items, categoryID = int(request.args.get("categoryID")))
    
@app.route("/login/", methods = ("GET", "POST"))
def login():
    if not session.get("username"):
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if not username:
                flash("Please enter a username!")
            elif not password:
                flash("Please enter a password!")
            else:
                result = list(users.find({"username": username}))
                if not result:
                    flash("Wrong password or username")
                else:
                    result = result[0]
                    if password != result["password"]:
                        flash("Wrong password or username")
                    else:
                        session["loggedIn"] = True
                        session["username"] = username
                        session["role"] = result["role"]["type"]
                        return redirect(url_for("index"))
        return render_template("login.html")
    else:
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    if session.get("username"):
        session["loggedIn"] = False
        session["username"] = None
        session["role"] = None
    return redirect(url_for("index"))

@app.route("/profile", methods = ("GET", "POST"))
def profile():
    global users, all_items
    if not session.get("username"):
        return redirect(url_for("login"))
    username = session["username"]
    avgRating = 0
    totalReviews = 0
    reviewList = []
    reviews = []
    allUsers = list(users.find())
    for user in allUsers:
        if user["username"] == username:
            avgRating = user["avgRating"]
            reviewList = user["reviews"]
            totalReviews = len(reviewList)
            break
    for review in reviewList:
        categoryID = review["categoryID"]
        productID = review["productID"]
        productName = ""
        for product in all_items[categoryID]:
            if product["itemID"] == productID:
                productName = product["itemName"]
                break
        reviews.append({"productName": productName, "reviewText": review["reviewText"]})
    if session.get("role") == "Admin":
        return render_template("profile.html", avgRating = avgRating, totalReviews = totalReviews, userReviews = reviews, users = allUsers)
    return render_template("profile.html", avgRating = avgRating, totalReviews = totalReviews, userReviews = reviews)
    

@app.route("/product", methods = ("GET", "POST"))
def product():
    global all_items
    if request.method == "POST":
        username = request.form["username"]
        productID = int(request.form["itemID"])
        categoryID = int(request.form["categoryID"])
        if request.form["submit_btn"] == "rev":
            reviewText = request.form["review"]
            if add_review(username, reviewText, productID, categoryID):
                categoriesList = list(categories.find())
                updatedItem = categoriesList[categoryID]
                all_items[categoryID] = []
                for item in updatedItem["items"]:
                    all_items[categoryID].append(item)
                return render_template("product.html", item = all_items[categoryID][find_product_idx(categoryID, productID)], categoryID = categoryID)
        elif request.form["submit_btn"] == "rate":
            rating = int(request.form["rating"])
            if add_rating(username, rating, productID, categoryID):
                categoriesList = list(categories.find())
                updatedItem = categoriesList[categoryID]
                all_items[categoryID] = []
                for item in updatedItem["items"]:
                    all_items[categoryID].append(item)
                return render_template("product.html", item = all_items[categoryID][find_product_idx(categoryID, productID)], categoryID = categoryID)
    productID = int(request.args.get("product"))
    categoryID = int(request.args.get("categoryID"))
    return render_template("product.html", item = all_items[categoryID][find_product_idx(categoryID, productID)], categoryID = categoryID)

@app.route("/deleteProduct", methods = ("GET", "POST"))
def deleteProduct():
    if session.get("role") == "Admin":
        productID = int(request.args.get("product"))
        categoryID = int(request.args.get("categoryID"))
        deleteProductHelper(productID, categoryID)
        return redirect(url_for("index"))
    return redirect(url_for("index"))

@app.route("/addProduct", methods = ("GET", "POST"))
def addProduct():
    global categories
    if session.get("role") == "Admin":
        if request.method == "POST":
            addProductHelper(int(request.args.get("categoryID")), request.form)
            return redirect(url_for("index"))
        return redirect(url_for("index"))
    return redirect(url_for("index"))
            
@app.route("/addUser", methods = ("GET", "POST"))
def addUser():
    global users
    if session.get("role") == "Admin":
        if request.method == "POST":
            newUsername = request.form["username"]
            newPassword = request.form["password"]
            newRole = request.form["role"]
            newRoleID = 1 if newRole == "User" else 0
            allUsers = list(users.find())
            flag = False
            for user in allUsers:
                if newUsername == user["username"]:
                    flash(f"User with username: {newUsername} already exists!")
                    flag = True
                    break
            if not flag:
                newID = allUsers[len(allUsers) - 1]["_id"] + 1
                users.insert_one(
                    {
                        "_id": newID,
                        "username": newUsername,
                        "password": newPassword,
                        "avgRating": 0,
                        "ratings": [],
                        "reviews": [],
                        "role": {
                            "roleID": newRoleID,
                            "type": newRole
                        }
                    }
                )
                flash(f"User with username: {newUsername} successfully inserted!")
            return redirect(url_for("profile"))
        return redirect(url_for("index"))
    return redirect(url_for("index"))

@app.route("/deleteUser", methods = ("GET", "POST"))
def deleteUser():
    global users
    if session.get("role") == "Admin":
        if request.method == "POST":
            flaggedUsername = request.form["username"]
            allUsers = list(users.find())
            idx = 0
            for user in allUsers:
                if user["username"] == flaggedUsername:
                    break
                idx += 1
            userReviews = allUsers[idx]["reviews"]
            userRatings = allUsers[idx]["ratings"]
            delRevRateFromProducts(userReviews, userRatings, flaggedUsername)
            users.delete_one(
                {
                    "_id": allUsers[idx]["_id"],
                    "username": flaggedUsername
                }
            )
            flash(f"User with username: {flaggedUsername} deleted successfully!")
            return redirect(url_for("profile"))
        return redirect(url_for("index"))
    return redirect(url_for("index"))

def delRevRateFromProducts(userReviews, userRatings, flaggedUsername):
    global all_items, categories
    for review in userReviews:
        categoryID = review["categoryID"]
        productID = review["productID"]
        idx = find_product_idx(categoryID, productID)
        rList = all_items[categoryID][idx]["reviews"]
        idxPR = 0
        for r in rList:
            if r["author"] == flaggedUsername:
                rList = rList[:idxPR] + rList[idxPR+1:]
                break
        categories.update_one(
            {
                "_id": categoryID,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.reviews": rList
                }
            }
        )
    
    for rating in userRatings:
        categoryID = rating["categoryID"]
        productID = rating["productID"]
        idx = find_product_idx(categoryID, productID)
        rList = all_items[categoryID][idx]["ratings"]
        idxPR = 0
        total_rating = 0
        for r in rList:
            if r["author"] == flaggedUsername:
                rList = rList[:idxPR] + rList[idxPR+1:]
                break
        for r in rList:
            total_rating += r["rating"]
        if len(rList) > 0:
            total_rating = total_rating / len(rList)
        categories.update_one(
            {
                "_id": categoryID,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.ratings": rList,
                    "items.$.rating": total_rating
                }
            }
        )
    
def find_product_idx(categoryID, productID):
    global all_items
    idx = 0
    for item in all_items[categoryID]:
        if item["itemID"] == productID:
            return idx
        idx += 1

def addProductHelper(categoryID, newProduct):
    global all_items, categories
    newItemID = 0
    if len(all_items[categoryID]) > 0:
        newItemID = all_items[categoryID][len(all_items[categoryID]) - 1]["itemID"] + 1
    newProductProcessed = None
    if categoryID == 0:
        newProductProcessed = {
            "itemID": newItemID,
            "itemName": newProduct["itemName"],
            "description": newProduct["description"],
            "price": newProduct["price"],
            "seller": newProduct["seller"],
            "image": newProduct["image"],
            "size": newProduct["size"],
            "colour": newProduct["colour"],
            "rating": 0,
            "ratings": [],
            "reviews": []
        }
    elif categoryID == 1:
        newProductProcessed = {
            "itemID": newItemID,
            "itemName": newProduct["itemName"],
            "description": newProduct["description"],
            "price": newProduct["price"],
            "seller": newProduct["seller"],
            "image": newProduct["image"],
            "rating": 0,
            "ratings": [],
            "reviews": [],
            "spec": newProduct["spec"]
        }
    elif categoryID == 2:
        newProductProcessed = {
            "itemID": newItemID,
            "itemName": newProduct["itemName"],
            "description": newProduct["description"],
            "price": newProduct["price"],
            "seller": newProduct["seller"],
            "image": newProduct["image"],
            "rating": 0,
            "ratings": [],
            "reviews": [],
            "spec": newProduct["spec"]
        }
    else:
        newProductProcessed = {
            "itemID": newItemID,
            "itemName": newProduct["itemName"],
            "description": newProduct["description"],
            "price": newProduct["price"],
            "seller": newProduct["seller"],
            "image": newProduct["image"],
            "rating": 0,
            "ratings": [],
            "reviews": []
        }
    categories.update_one(
        {
            "_id": categoryID
        },
        {
            "$push": {
                "items": newProductProcessed
            }
        }
    )
    categoriesList = list(categories.find())
    updatedItem = categoriesList[categoryID]
    all_items[categoryID] = []
    for item in updatedItem["items"]:
        all_items[categoryID].append(item)

def deleteProductHelper(productID, categoryID):
    global all_items, categories
    deleteProductInfoFromUser(productID, categoryID)
    idx = 0
    for product in all_items[categoryID]:
        if product["itemID"] == productID:
            all_items[categoryID] = all_items[categoryID][:idx] + all_items[categoryID][idx + 1:]
            break
        idx += 1
    categories.update_one(
        {
            "_id": categoryID
        },
        {
            "$set": {
                "items": all_items[categoryID]
            }
        }
    )

def deleteProductInfoFromUser(productID, categoryID):
    global users
    allUsers = list(users.find())
    for user in allUsers:
        reviewList = user["reviews"]
        ratingList = user["ratings"]
        deleteRevRateFromUser(reviewList, ratingList, productID, categoryID, user["_id"])

def deleteRevRateFromUser(reviewList, ratingList, productID, categoryID, userID):
    global users
    idx = 0
    for review in reviewList:
        if review["productID"] == productID and review["categoryID"] == categoryID:
            reviewList = reviewList[:idx] + reviewList[idx + 1:]
            break
        idx += 1
    idx, totalRating = 0, 0
    for rating in ratingList:
        if rating["productID"] == productID and rating["categoryID"] == categoryID:
            ratingList = ratingList[:idx] + ratingList[idx + 1:]
            break
        idx += 1
    if ratingList:
        for rating in ratingList:
            totalRating += rating["rating"]
        totalRating = totalRating / len(ratingList)
    users.update_one(
        {
            "_id": userID
        },
        {
            "$set": {
                "reviews": reviewList,
                "ratings": ratingList,
                "avgRating": totalRating
            }
        }
    )

def add_review(username, reviewText, productID, categoryID):
    global all_items, categories
    reviewList = all_items[categoryID][find_product_idx(categoryID, productID)]["reviews"]
    idx, flag = 0, False
    for review in reviewList:
        if review["author"] == username:
            flag = True
            break
        idx += 1
    if flag:
        all_items[categoryID][find_product_idx(categoryID, productID)]["reviews"][idx]["reviewText"] = reviewText
        categories.update_one(
            {
                "_id": categoryID,
                "items.itemID": productID
            },
            {
                "$set": {
                    "items.$.reviews": all_items[categoryID][find_product_idx(categoryID, productID)]["reviews"]
                }
            }
        )
    else:
        lastReviewID = -1
        if len(reviewList) > 0:
            lastReviewID = reviewList[len(reviewList) - 1]["reviewID"]
        newReview = {"reviewID": lastReviewID + 1, "reviewText": reviewText, "author": username}
        categories.update_one(
            {
                "_id": categoryID,
                "items.itemID": productID
            },
            {
                "$push": {
                    "items.$.reviews": newReview
                }
            }
        )
    addReviewUser(productID, categoryID, reviewText, username)
    return True

def add_rating(username, rating, productID, categoryID):
    global all_items, categories
    ratingList = all_items[categoryID][find_product_idx(categoryID, productID)]["ratings"]
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
                "_id": categoryID,
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
        lastRatingID = -1
        if len(ratingList) > 0:
            lastRatingID = ratingList[len(ratingList) - 1]["ratingID"]
        ratingCount = len(ratingList)
        for ratings in ratingList:
            totalRating += ratings["rating"]
        avgRating = (totalRating + rating) / (ratingCount + 1)
        newRating = {"ratingID": lastRatingID + 1, "rating": rating, "author": username}
        categories.update_one(
            {
                "_id": categoryID,
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
    addRatingUser(productID, categoryID, rating, username)
    return True

def addReviewUser(productID, categoryID, reviewText, username):
    global users
    allUsers = list(users.find())
    idxUser = 0
    for user in allUsers:
        if user["username"] == username:
            break
        idxUser += 1
    reviewList = allUsers[idxUser]["reviews"]
    idx, flag = 0, False
    for review in reviewList:
        if review["categoryID"] == categoryID and review["productID"] == productID:
            flag = True
            break
        idx += 1
    if flag:
        allUsers[idxUser]["reviews"][idx]["reviewText"] = reviewText
        users.update_one(
            {
                "username": username
            },
            {
                "$set": {
                    "reviews": allUsers[idxUser]["reviews"]
                }
            }
        )
    else:
        lastReviewID = -1
        if reviewList:
            lastReviewID = reviewList[len(reviewList) - 1]["reviewID"]
        newReview = {"reviewID": lastReviewID + 1, "productID": productID, "reviewText": reviewText, "categoryID": categoryID}
        print(newReview)
        users.update_one(
            {
                "username": username
            },
            {
                "$push": {
                    "reviews": newReview
                }
            }
        )
    return True

def addRatingUser(productID, categoryID, rating, username):
    global users
    allUsers = list(users.find())
    idxUser = 0
    for user in allUsers:
        if user["username"] == username:
            break
        idxUser += 1
    ratingList = allUsers[idxUser]["ratings"]
    idx, flag, totalRating = 0, False, 0
    print(categoryID)
    for ratingElement in ratingList:
        if ratingElement["categoryID"] == categoryID and ratingElement["productID"] == productID:
            flag = True
            break
        idx += 1
    if flag:
        allUsers[idxUser]["ratings"][idx]["rating"] = rating
        for ratingElement in ratingList:
            totalRating += ratingElement["rating"]
        totalRating = totalRating / len(ratingList)
        users.update_one(
            {
                "username": username
            },
            {
                "$set": {
                    "ratings": allUsers[idxUser]["ratings"],
                    "avgRating": totalRating
                }
            }
        )
    else:
        lastRatingID = -1
        if ratingList:
            lastRatingID = ratingList[len(ratingList) - 1]["ratingID"]
        newRating = {"ratingID": lastRatingID + 1, "rating": rating, "productID": productID, "categoryID": categoryID}
        for ratingElement in ratingList:
            totalRating += ratingElement["rating"]
        totalRating += rating
        totalRating = totalRating / (len(ratingList) + 1)
        users.update_one(
            {
                "username": username
            },
            {
                "$push": {
                    "ratings": newRating
                },
                "$set": {
                    "avgRating": totalRating
                }
            }
        )
    return True