from pymongo import MongoClient

# MongoDB connection URI
MONGO_URI = "mongodb://10.10.0.3:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.1"
DATABASE_NAME = "mantis"

# Create a MongoClient instance
client = MongoClient(MONGO_URI)

# Access the mantis database
db = client[DATABASE_NAME]

Assets_collection = db["assets_collection"]
Findings_collection = db["findings_collection"]
users_collection = db["users_collection"]
