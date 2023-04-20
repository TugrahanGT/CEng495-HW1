# User Manual
	- The render URL: https://gokcwnify.onrender.com/
	- There is a sticky navbar at the top of the page that allows users to navigate through the page. For logging in and registering  
	operations, there are two buttons at the right of the navbar "Log In" and "Register". Using these buttons, one can create a user  
	and log in afterwards. Moreover, there is a button at the end of the Log In page that allows a redirection to the register page  
	if user has no registration on our application. The logo and home button works as the same, just redirecting to the home page.  
	After logging in, these two buttons change to "'username'" and "Log Out", respectively. One can go to the profile page by clicking  
	their username at the top, or log out using the log out button.
	- In the home page, there is a navbar located at the left of the page that allows users to browse items regarding their category.  
	If no category is selected, all items will be present in this page. For each item, we have a card defined. In the end of the card,  
	there are one button to view the product. If the current user has an admin priviledge, then there will appear another button called  
	"Delete", which allows admin to delete products easily. 
	- In the product page, the page is divided into 4 cards. The first card takes more space than the others. In the first card, it shows  
	the product information. The 3 cards that follow the product information are for reviews of the product, writing a review and giving  
	a rating. However, writing a review and giving a rating will only be active when a user is logged in. If no user is currently logged  
	in to the page, only reviews of the product will be shown.
# Logging as Admin User
	There is an admin user created for testing purposes:
		- Username: cloudAdmin
		- Password: cloud495
	One can log in as an admin user using these credientials and try the admin functionalities. For logging in as a regular user  
	you can simply follow the register page and create a user. However, there is also a test user present, which has the  
	credientials:
		- Username: testUser
		- Password: cloud495

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
		1. Flask: I have utilized functionalities that Flask provides to make our web service working. Using Flask-Session,  
		I have designed a session based service, which allows multiple unique sessions for different browsers. This functionality  
		is designed and required for different Log-In and view processes. Moreover, since Flask is an easy option to  
		define routes and functions for routers in Python, it was the best choice for such application. Moreover, Flask utilizes  
		Jinja which helps us to parse HTML files and pass variables between those two. So, I have prepared HTML pages for the  
		web application and have utilized the connection between the Flask and HTML page. There are 6 web pages available for  
		use. Moreover, all of the pages have a navbar to make logging in and registering or navigating through the page possible.  
			- index.html: This web page is the home page, where all products are shown to any user. If no categories are selected,  
			all items belonging to all categories will be present in this page. In the left navigation bar, we have a category selector  
			which allows users to browse items regarding the selected category.
			- product.html: The product page is a skeleton for item viewing page. There is a single product.html file defined and  
			using Jinja template functionalities, I am passing the categoryID and productID attributes to this html file and  
			parse the product using this information. This functionality has given me the opportunity to define one dynamic page  
			for any product.
			- profile.html: The profile page is again dynamically designed for any user information. However, there is a slight change.  
			In the profile page, if the current user has the admin priviledges, a different list will appear which enables admin  
			functionalities. The functionalities of the admin user as the same as the minimum requirements of the homework.  
			- login.html/register.html: These two files are the nearly exact copies each other, however, they have different form  
			actions. Login file sends the form information to the login route, and the register page sends it to the createUser  
			route. 
		There are added routes which does not redirect to their own page, instead they are redirecting to the home page whenever  
		their operations are done. For example, in the all of the admin operations, if the operation is successful, the page is  
		redirected to the index page to see the difference made. There are routes that are not visible and I will count them in the  
		following list.
			* /addUser: This route is defined for admin panel user creation. When the add user form is submitted from the admin panel,  
			the information to be added will be passed to this route and then used to create the user. If a user with same username does  
			not exist and the creation operation is successful, then the page is redirected to the home page. However, if the operation  
			is not successful, then the route redirects to the same profile page with an error message showing what went wrong. All of the  
			following routes that have no explanation work in the same fashion to this route.
			* /deleteUser,
			* /deleteProduct,
			* /addProduct,
			* /createUser: This route is defined for user register form. When a user tries to register using the register page, the  
			submitted information is passed to this route. Again, a similar if check is being used to control if such user exists, and  
			if operation is successful the user is redirected to the login page. However, if operation is not successful, then it  
			redirects to the register page with an error indicating what went wrong.
		All of the routes explained above are implemented functionalities that PyMongo provides to us. Since I have defined products  
		as an array of objects in MongoDB, the operations on such entities are basic array operations. Deleting will be a simple  
		removing from index and adding is a simple pushing method. However, when a user adds a review or rating, then we have an  
		update within two collections. It basically updates the review or rating list of the user and product. 
