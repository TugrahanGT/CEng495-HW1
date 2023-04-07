// Creating the db for the project
use("hw1_mongoDB");

// Create roles collection for users
db.getCollection("roles").insertMany([
    {"type": "Admin"},
    {"type": "User"},
]);

// Create user collection
db.getCollection("users").insertMany([
    {"userName": "admin", "password": "admin", "roleId": 0},
    {"userName": "basic", "password": "12345", "roleId": 1},
]);


