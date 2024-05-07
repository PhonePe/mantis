from fastapi import APIRouter, HTTPException, status, Query, Security
from pymongo import MongoClient
import io
import pandas as pd
from fastapi.responses import StreamingResponse
from routes.login_reg import get_current_user
from models.user import User
from typing import Annotated
from config.db import db, Assets_collection, Findings_collection
#outer details
router = APIRouter(prefix="/network_information", tags=["network_information"])

#mongo connect client 
# client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.1")


# #mongodb details
# db = client["mantis"]
# Assets_collection = db["assets_collection"]
# Findings_collection = db["findings_collection"]


#table route
@router.get("/asn_name_count_q", status_code=status.HTTP_200_OK)
async def asn_name_count_q(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$unwind": "$as_name"},
        {"$group": {"_id": "$as_name", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "x": "$_id", "y": "$count"}}
    ]

    result = list(Assets_collection.aggregate(pipeline))
    
    return result

@router.get("/country_based_ip_count", status_code=status.HTTP_200_OK)
async def country_based_ip_count(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": {"$nin": ["certificate"]}}},
        {"$project": {"countries": {"$objectToArray": "$ipinfo"}}},
        {"$unwind": "$countries"},
        {"$group": {"_id": "$countries.v.country_name", "count": {"$sum": 1}}},
        {
            "$project": {
                "_id": 0,
                "x": {"$ifNull": ["$_id", "NULL"]},
                "y": "$count"
            }
        }
    ]

    result = list(Assets_collection.aggregate(pipeline))
    
    return result

@router.get("/asn_count_q", status_code=status.HTTP_200_OK)
async def asn_count_q(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$unwind": "$as_number"},
        {"$group": {"_id": "$as_number", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "x": "$_id", "y": "$count"}}
    ]

    result = list(Assets_collection.aggregate(pipeline))
    
    return result

@router.get("/asn_country_count_q", status_code=status.HTTP_200_OK)
async def asn_country_count_q(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$unwind": "$as_country"},
        {"$group": {"_id": "$as_country", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "x": "$_id", "y": "$count"}}
    ]


    result = list(Assets_collection.aggregate(pipeline))
    
    return result

@router.get("/ipSearch", status_code=status.HTTP_200_OK)
async def ipSearch(
    current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read", "write"])],
    org: str = Query(None, description="Organization name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Items per page"),
    search_column: str = Query(None, description="Column name to search on"),
    search_term: str = Query(None, description="Term to search for")
):
    match_stage = {}
    if org:
        match_stage["org"] = org

    # Handle search functionality
    if search_column and search_term:
        match_stage[search_column] = {"$regex": f".*{search_term}.*", "$options": "i"}  # Case-insensitive substring search

    pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": {"$ne": "certificate"}}},
        {"$project": 
            {"org": "$org", "asset": "$asset", "ipinfo": {"$objectToArray": "$ipinfo"}}},
        {"$unwind": "$ipinfo"},
        {"$project": {
            "_id": False,
            "Org": "$org",
            "Asset": "$asset",
            "IP": "$ipinfo.k",
            "IP Country": "$ipinfo.v.country_name",
            "IP Latitude": "$ipinfo.v.ip_location.lat",
            "IP Longitude": "$ipinfo.v.ip_location.long"
        }},
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size}
    ]

    # Count total records matching the query
    total_records_pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": {"$ne": "certificate"}}},
        {"$group": {"_id": None, "total": {"$sum": 1}}}
    ]
    
    total_records_result = list(Assets_collection.aggregate(total_records_pipeline))
    total_records = total_records_result[0]["total"] if total_records_result else 0

    # Get paginated data
    result = list(Assets_collection.aggregate(pipeline))

    return {"total_records": total_records, "data": result}




@router.get("/asnSearch", status_code=status.HTTP_200_OK)
async def search(
    current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read", "write"])],
    org: str = Query(None, description="Organization name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Items per page"),
    search_column: str = Query(None, description="Column name to search on"),
    search_term: str = Query(None, description="Term to search for")
):
    match_stage = {}
    if org:
        match_stage["org"] = org

    # Handle search functionality
    if search_column and search_term:
        match_stage[search_column] = {"$regex": f".*{search_term}.*", "$options": "i"}  # Case-insensitive substring search

    pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": {"$ne": "certificate"}}},
        {"$project": {
            "_id": False,
            "Org": "$org",
            "Asset": "$asset",
            "ASN Number": "$as_number",
            "ASN Country": "$as_country",
            "ASN Range": "$as_range"
        }},
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size}
    ]

    # Count total records matching the query
    total_records_pipeline = [
            {"$match": match_stage},
            {"$match": {"asset_type": {"$ne": "certificate"}}},
            {"$group": {"_id": None, "total": {"$sum": 1}}}
        ]
    total_records_result = list(Assets_collection.aggregate(total_records_pipeline))
    total_records = total_records_result[0]["total"] if total_records_result else 0
        # Get paginated data
    result = list(Assets_collection.aggregate(pipeline))

    return {"total_records": total_records, "data": result}


@router.get("/ipDownload_csv", status_code=status.HTTP_200_OK)
async def ipDownload_csv(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(..., description="Organization name")):
  match_stage = {"org": org}

  pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": {"$ne": "certificate"}}},
        {"$project": 
            {"org": "$org", "asset": "$asset", "ipinfo": {"$objectToArray": "$ipinfo"}}},
        {"$unwind": "$ipinfo"},
        {"$project": {
            "_id": False,
            "Org": "$org",
            "Asset": "$asset",
            "IP": "$ipinfo.k",
            "IP Country": "$ipinfo.v.country_name",
            "IP Latitude": "$ipinfo.v.ip_location.lat",
            "IP Longitude": "$ipinfo.v.ip_location.long"
        }}
    ]

  result = list(Assets_collection.aggregate(pipeline))

  df = pd.DataFrame(result)  # Convert data to a DataFrame
  csv_file = io.StringIO()  # Create an in-memory file-like object
  df.to_csv(csv_file, index=False)  # Write the DataFrame to the CSV file

  # Return the CSV file as a streaming response
  return StreamingResponse(
    io.BytesIO(csv_file.getvalue().encode("utf-8")),
    media_type="text/csv",
    headers={"Content-Disposition": f"attachment; filename=ipInfo_{org}.csv"}
  )

@router.get("/asnDownload_csv", status_code=status.HTTP_200_OK)
async def asnDownload_csv(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(..., description="Organization name")):
  match_stage = {"org": org}

  pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": {"$ne": "certificate"}}},
        {"$project": {
            "_id": False,
            "Org": "$org",
            "Asset": "$asset",
            "ASN Number": "$as_number",
            "ASN Country": "$as_country",
            "ASN Range": "$as_range"
        }}
    ]
  result = list(Assets_collection.aggregate(pipeline))

  df = pd.DataFrame(result)  # Convert data to a DataFrame
  csv_file = io.StringIO()  # Create an in-memory file-like object
  df.to_csv(csv_file, index=False)  # Write the DataFrame to the CSV file

  # Return the CSV file as a streaming response
  return StreamingResponse(
    io.BytesIO(csv_file.getvalue().encode("utf-8")),
    media_type="text/csv",
    headers={"Content-Disposition": f"attachment; filename=asnInfo_{org}.csv"}
  )


