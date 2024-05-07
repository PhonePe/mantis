from fastapi import APIRouter, HTTPException, status, Query, Security
from pymongo import MongoClient
import io
import pandas as pd
from fastapi.responses import StreamingResponse
from routes.login_reg import get_current_user
from models.user import User
from typing import Annotated
from config.db import db, Assets_collection, Findings_collection
router = APIRouter(prefix="/certificates", tags=["certificates"])


# client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.1")


# #mongodb details
# db = client["mantis"]
# Assets_collection = db["assets_collection"]
# Findings_collection = db["findings_collection"]

#table
@router.get("/search", status_code=status.HTTP_200_OK)
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
        {"$match": {"asset_type": "certificate"}},
        {
            "$project": {
                "_id": "$_id",
                "Created": "$created_timestamp",
                "Asset": "$asset",
                "Org": "$org",
                "PubKey_SHA256": "$others.pubkey_sha256",
                "DNS_Names": {"$reduce": {
                    "input": "$others.dns_names",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$others.dns_names", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "$$this"]},
                            "else": {"$concat": ["$$value", ", ", "$$this"]}
                        }
                    }
                }},
                "Issuer": "$others.issuer.friendly_name",
                "Valid Till": "$others.not_after",
                "Status": "$status",
                "Modified By": "$modified_by"
            }
        },
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size}
    ]

    result = list(Assets_collection.aggregate(pipeline))
    
    # Modify total_records_pipeline to include pagination
    total_records_pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": "certificate"}},
        {"$group": {"_id": None, "total": {"$sum": 1}}}
    ]

    total_records_result = list(Assets_collection.aggregate(total_records_pipeline))
    total_records = total_records_result[0]["total"] if total_records_result else 0

    return {"total_records": total_records, "data": result}

@router.get("/total", status_code=status.HTTP_200_OK)
async def total_count(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": "certificate"}},
        {
            "$group": {
                "_id": None,
                "count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_count": "$count"
            }
        }
    ]

    result = list(Assets_collection.aggregate(pipeline))
    
    return result

@router.get("/certs_issuer_chart", status_code=status.HTTP_200_OK)
async def certs_issuer_chart(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": "certificate"}},
        {"$project": {
            "_id": False,
            "Asset": "$asset",
            "Org": "$org",
            "PubKey_SHA256": "$others.pubkey_sha256",
            "DNS_Names": {
                "$reduce": {
                    "input": "$others.dns_names",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$others.dns_names", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "$$this"]},
                            "else": {"$concat": ["$$value", ", ", "$$this"]}
                        }
                    }
                }
            },
            "Issuer": "$others.issuer.friendly_name",
            "Valid Till": "$others.not_after"
        }},
        {"$group": {
            "_id": {"Issuer": "$Issuer"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "x": "$_id.Issuer", "y": "$count"}}
    ]

    # Get data
    result = list(Assets_collection.aggregate(pipeline))

    return result

@router.get("/download_csv", status_code=status.HTTP_200_OK)
async def vulnerability_download_csv(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(..., description="Organization name")):
  match_stage = {"org": org}

  pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": "certificate"}},
        {
            "$project": {
                "_id": "$_id",
                "Created": "$created_timestamp",
                "Asset": "$asset",
                "Org": "$org",
                "PubKey_SHA256": "$others.pubkey_sha256",
                "DNS_Names": {"$reduce": {
                    "input": "$others.dns_names",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$others.dns_names", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "$$this"]},
                            "else": {"$concat": ["$$value", ", ", "$$this"]}
                        }
                    }
                }},
                "Issuer": "$others.issuer.friendly_name",
                "Valid Till": "$others.not_after",
                "Status": "$status",
                "Modified By": "$modified_by"
            }
        }
    ]

  result = list(Assets_collection.aggregate(pipeline))

  df = pd.DataFrame(result)  # Convert data to a DataFrame
  csv_file = io.StringIO()  # Create an in-memory file-like object
  df.to_csv(csv_file, index=False)  # Write the DataFrame to the CSV file

  # Return the CSV file as a streaming response
  return StreamingResponse(
    io.BytesIO(csv_file.getvalue().encode("utf-8")),
    media_type="text/csv",
    headers={"Content-Disposition": f"attachment; filename=cert_{org}.csv"}
  )