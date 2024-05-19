from fastapi import APIRouter, HTTPException, status, Query, Security
from pymongo import MongoClient
import io
import pandas as pd
from fastapi.responses import StreamingResponse
from routes.login_reg import get_current_user
from models.user import User
from typing import Annotated
from config.db import db, Assets_collection, Findings_collection

router = APIRouter(prefix="/phishing_domain", tags=["phishing_domain"])

 

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
        {"$match": {"type": "phishing"}},
        {
            "$project": {
                "Created": "$created_timestamp",
                "_id": "$_id",
                "Host": "$host",
                "Possible Phishing Url": "$url",
                "Title": "$title",
                "Org": "$org",
                "App": "$app",
                "Description": "$info.description",
                "Severity": "$info.severity",
                "Tool Source": "$tool_source",
                "Falsepositive": "$falsepositive",
                "Status Code": "$others.status_code",
                "Probability": "$others.probability",
                "Status": "$status",
                "Modified By": "$modified_by"
            }
        },
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size}
    ]

    total_records_pipeline = [
        {"$match": match_stage},
        {"$match": {"type": "phishing"}},
        {"$group": {"_id": None, "total": {"$sum": 1}}}
    ]
    total_records_result = list(Findings_collection.aggregate(total_records_pipeline))
    total_records = total_records_result[0]["total"] if total_records_result else 0
    # Get paginated data
    result = list(Findings_collection.aggregate(pipeline))

    return {"total_records": total_records, "data": result}

#total Phishing count
@router.get("/total", status_code=status.HTTP_200_OK)
async def total_count(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},  # Match stage for filtering based on org if provided
        {"$match": {"type": "phishing"}},  # Match stage for filtering based on type
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


#phishing_by_app_chart
@router.get("/phishing_by_app_chart", status_code=status.HTTP_200_OK)
async def phishing_by_app_chart(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$match": {"type": "phishing"}},
        {
            "$group": {
                "_id": {"app": "$app"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "x": "$_id.app",
                "y": "$count"
            }
        }
    ]

    result = list(Findings_collection.aggregate(pipeline))
    
    return result

@router.get("/download_csv", status_code=status.HTTP_200_OK)
async def vulnerability_download_csv(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(..., description="Organization name")):
  match_stage = {"org": org}

  pipeline = [
        {"$match": match_stage},
        {"$match": {"type": "phishing"}},
        {
            "$project": {
                "Created": "$created_timestamp",
                "_id": "$_id",
                "Host": "$host",
                "Possible Phishing Url": "$url",
                "Title": "$title",
                "Org": "$org",
                "App": "$app",
                "Description": "$info.description",
                "Severity": "$info.severity",
                "Tool Source": "$tool_source",
                "Falsepositive": "$falsepositive",
                "Status Code": "$others.status_code",
                "Probability": "$others.probability",
                "Status": "$status",
                "Modified By": "$modified_by"
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
    headers={"Content-Disposition": f"attachment; filename=phishingDomain_{org}.csv"}
  )