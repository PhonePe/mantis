from fastapi import APIRouter, HTTPException, status, Query
from pymongo import MongoClient
from config.db import db, Assets_collection, Findings_collection

router = APIRouter(prefix="/org", tags=["org details"])

# client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.1")


# #mongodb details
# db = client["mantis"]
# Assets_collection = db["assets_collection"]
# Findings_collection = db["findings_collection"]

@router.get("/organizations", status_code=status.HTTP_200_OK)
async def get_organizations():
    # Retrieve all unique organization names from the collection
    org_names = Assets_collection.distinct("org")

    # Return the unique organization names as JSON response
    return org_names