from fastapi import APIRouter, HTTPException, status, Query, Security 
from pymongo import MongoClient
import re

import io
import pandas as pd
from fastapi.responses import StreamingResponse
from routes.login_reg import get_current_user
from models.user import User
from typing import Annotated, Optional, List
from config.db import db, Assets_collection, Findings_collection

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])

  





#vulnerabilities_severity api route
@router.get("/severity", status_code=status.HTTP_201_CREATED)
async def vulnerabilities_severity(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {
            "$match": {"type": "vulnerability"}
        },
        {
            "$group": {
                "_id": {
                    "severity": "$info.severity"
                },
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {
                "_id.severity": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "x": {"$ifNull": ["$_id.severity", "NULL"]},
                "y": "$count"
            }
        }
    ]

    result = list(Findings_collection.aggregate(pipeline))
    print(result)

    return result

#total_count api route
@router.get("/total_count", status_code=status.HTTP_200_OK)
async def total_count(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$match": {"type": "vulnerability"}},
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

    result = list(Findings_collection.aggregate(pipeline))
    
    return result


#vulnerability_title api route
@router.get("/vulnerability_title", status_code=status.HTTP_200_OK)
async def vulnerability_title(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$match": {"type": "vulnerability"}},
        {
            "$group": {
                "_id": {"title": "$title"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.title": 1}},
        {
            "$project": {
                "_id": 0,
                "x": "$_id.title",
                "y": "$count"
            }
        }
    ]

    result = list(Findings_collection.aggregate(pipeline))

    return result

#vulnerability_table api route
@router.get("/vulnerability_table", status_code=status.HTTP_200_OK)
async def vulnerability_table(
    current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])],
    org: str = Query(None, description="Organization name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Items per page")
):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$match": {"type": "vulnerability"}},
        {
            "$project": {
                "Created": "$created_timestamp",
                "_id": "$_id",
                "Host": "$host",
                "Title": "$title",
                "Org": "$org",
                "App": "$app",
                "Url": "$url",
                "Description": "$info.description",
                "Severity": "$info.severity",
                "Tool Source": "$tool_source",
                "Remediation": "$remediation",
                "Status": "$status",
                "Modified By": "$modified_by",
                "Updated Timestamp": "$updated_timestamp"
            }
        },
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size}
    ]

    total_records_pipeline = [
            {"$match": match_stage},
            {"$match": {"type": "vulnerability"}},
            {"$group": {"_id": None, "total": {"$sum": 1}}}
        ]
    total_records_result = list(Findings_collection.aggregate(total_records_pipeline))
    total_records = total_records_result[0]["total"] if total_records_result else 0
        # Get paginated data
    result = list(Findings_collection.aggregate(pipeline))

    return {"total_records": total_records, "data": result}

@router.get("/download_csv", status_code=status.HTTP_200_OK)
async def vulnerability_download_csv(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(..., description="Organization name")):
  match_stage = {"org": org}

  pipeline = [
    {"$match": match_stage},
    {"$match": {"type": "vulnerability"}},
    {
      "$project": {
        "Created": "$created_timestamp",
        "_id": "$_id",
        "Host": "$host",
        "Title": "$title",
        "Org": "$org",
        "App": "$app",
        "Url": "$url",
        "Description": "$info.description",
        "Severity": "$info.severity",
        "Tool Source": "$tool_source",
        "Remediation": "$remediation",
        "Status": "$status",
        "Modified By": "$modified_by",
        "Updated Timestamp": "$updated_timestamp"
      }
    }
  ]

  result = list(Findings_collection.aggregate(pipeline))

  df = pd.DataFrame(result)  # Convert data to a DataFrame
  csv_file = io.StringIO()  # Create an in-memory file-like object
  df.to_csv(csv_file, index=False)  # Write the DataFrame to the CSV file

  # Return the CSV file as a streaming response
  return StreamingResponse(
    io.BytesIO(csv_file.getvalue().encode("utf-8")),
    media_type="text/csv",
    headers={"Content-Disposition": f"attachment; filename=vulnerabilities_{org}.csv"}
  )


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
        {"$match": {"type": "vulnerability"}},
        {
            "$project": {
                "Created": "$created_timestamp",
                "_id": "$_id",
                "Host": "$host",
                "Title": "$title",
                "Org": "$org",
                "App": "$app",
                "Url": "$url",
                "Description": "$info.description",
                "Severity": "$info.severity",
                "Tool Source": "$tool_source",
                "Remediation": "$remediation",
                "Status": "$status",
                "Modified By": "$modified_by",
                "Updated Timestamp": "$updated_timestamp"
            }
        },
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size}
    ]

    total_records_pipeline = [
            {"$match": match_stage},
            {"$match": {"type": "vulnerability"}},
            {"$group": {"_id": None, "total": {"$sum": 1}}}
        ]
    total_records_result = list(Findings_collection.aggregate(total_records_pipeline))
    total_records = total_records_result[0]["total"] if total_records_result else 0

    # Get paginated data
    result = list(Findings_collection.aggregate(pipeline))

    return {"total_records": total_records, "data": result}
