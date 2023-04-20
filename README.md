# Design Options
## 1. MongoDB
	In MongoDB, and NoSQL structure, I have decided on using
	two collections: finalizedCategories and users. Since MongoDB
	uses a dynamic schema, using only these collections seemed
	enough for our homework. Below are the explanations of the
	collections and which attribute each collection has.
	1. finalizedCategories:
		Attributes:
			{
				"_id": Integer,
				"name": String (Name of the category),
				"items": [
					"itemID": Integer,
					"itemName": String (Name of the item),
					"description": String (Description of the item),
					"price": Integer (Price of the item),
					"seller": String (Seller of the item),
					"image": String (A hyperlink to the image of the item)
					"size": String (For only clothings category),
					"colour": String (For only clothings category),
					"spec": String (For only computer components and monitor categories),
					"rating": Integer (Represents the average rating of the item),
					"ratings": [
						"ratingID": Integer,
						"rating": Integer (Rating value that a user provided for the item),
						"author": String (Username belonging to the rating)
					],
					"reviews": [
						"reviewID": Integer,
						"reviewText": String (Review value that a user provided for the item),
						"author": String (Username belonging to the review)
					]
				]
			}
		There are 4 categories in finalizedCategories collection; clothings, computer components,
		monitors, and snacks. For each category, there is an items array (array of item objects) attached
		to it representing the items belonging to that category. Again, for each item there are their own
		attributes with	ratings and reviews attributes added. This addition exists to keep track on the
		reviews and the ratings of each item. The two attributes again are defined as an array of objects,
		having their own attributes as can be seen from above. The average rating of an item is calculated
		when a user provides a rating to the item. Once the rating list of the item is updated, then the
		average rating value is updated also. However, including ratings and reviews to the categories,
		and ultimately to the items, resulted in O(n^2) operations when matching those with users. This will
		be explained once the users collection explanation is done.
	2. users:
		Attributes:
			{
				"_id": Integer,
				"username": String (Username of the user, utilized in logging, should be unique)
				"password": String (Password of the user),
				"avgRating": Integer (Average rating provided by the user),
				"role": {
					"roleID": Integer,
					"type": String (Represents the type of the role, takes two values: 'Admin' and 'User')
				},
				"ratings": [
					"ratingID": Integer,
					"rating": Integer (Rating value that the user provided for an item),
					"productID": Integer (ID of the product that has been rated),
					"categoryID": Integer (Category ID of the product that it belongs to)
				],
				"reviews": [
					"reviewID": Integer,
					"reviewText": String (Review value that the user provided for an item),
					"productID": Integer (ID of the product that has been rated),
					"categoryID": Integer (Category ID of the product that it belongs to)
				]
			}
		The users collection is defined as simple as it can be. In its attributes, one can recognize a role
		object. This object helps us to keep track of the priviledges of the user while surfing through our
		application. There are two differents of roles defined: Admin and User. Each role has the capabilities
		that it should have according to our homework. On the other hand, it can also be recognizable that
		reviews and ratings attributes for the users collection are also defined. That is the problem that was
		mentioned while explaining the finalizedCategories collection. The thing is, when adding or deleting a
		review/rating, we should make a update on both of these collections. The only negative aspect of such
		operation is that, as the list of ratings or reviews gets larger, the operations may take some more time.
		However, in practice, this should not be a problem.
	These two collections finalizes our MongoDB structure. The aim of designing and degrading the collection
	count to 2 was to make use of the dynamic schema MongoDB provides to us.
## 2. Web Application
	In web application, I have used several different libraries to make it functional and serve its purpose
	to the users. The libraries I have used are: Flask, PyMongo, Gunicorn, and Flask-Session. Flask and
	Flask-Session are being used as a microservice for our web application. PyMongo is being used to connect
	and utilize our MongoDB, and Gunicorn is being used to serve the Flask application. For the front-end design,
	I have used basic Bootstrap to make our website look a little bit good since I have no creativity on designing
	good visual items. For our website, we have 5 routes available to any user, and 5 routes that are not available
	and only called when certain operations are done. I will go on with explaining what each route (and their
	respective functions) does and why I have used Flask with Flask-Session.

