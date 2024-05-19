from fastapi import APIRouter, HTTPException, status, Query
from pymongo import MongoClient
from config.db import db, Assets_collection, Findings_collection

router = APIRouter(prefix="/org", tags=["org details"])

 

@router.get("/organizations", status_code=status.HTTP_200_OK)
async def get_organizations():
    # Retrieve all unique organization names from the collection
    org_names = Assets_collection.distinct("org")

    # Return the unique organization names as JSON response
    return org_names