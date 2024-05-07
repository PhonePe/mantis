from fastapi import APIRouter, HTTPException, status, Query, Security
from pymongo import MongoClient
import io
import pandas as pd
from fastapi.responses import StreamingResponse
from routes.login_reg import get_current_user
from models.user import User
from typing import Annotated
from config.db import db, Assets_collection, Findings_collection

router = APIRouter(prefix="/secrets", tags=["secrets"])

# client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.1")


# #mongodb details
# db = client["mantis"]
# Assets_collection = db["assets_collection"]
# Findings_collection = db["findings_collection"]

@router.get("/total_count", status_code=status.HTTP_200_OK)
async def total_count(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$match": {"type": "secret"}},
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

#table secret
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
  {
    "$match": {
      "type": "secret"
    }
  },
  {
    "$project": {
			"Created": "$created_timestamp",
      "_id": "$_id",
      "Host": "$host",
      "Url": "$url",
      "Title": "$title",
      "Org": "$org",
      "Description": "$info.description",
      "Severity": "$info.severity",
      "Tool Source": "$tool_source",
      "Falsepositive": "$falsepositive",
			"Rule Id": "$info.RuleID",
			"Key" : "$info.key", 
			"Match" : "$info.Match",
			"Status": "$status",
			"Modified By": "$modified_by"
			
    }
  },
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size}
    ]

    total_records_pipeline = [
        {"$match": match_stage},
        {"$match": {"type": "secret"}},
        {"$group": {"_id": None, "total": {"$sum": 1}}}
    ]
    total_records_result = list(Findings_collection.aggregate(total_records_pipeline))
    total_records = total_records_result[0]["total"] if total_records_result else 0
    # Get paginated data
    result = list(Findings_collection.aggregate(pipeline))

    return {"total_records": total_records, "data": result}

#rule_id api route
@router.get("/rule_id", status_code=status.HTTP_201_CREATED)
async def vulnerabilities_severity(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
	{
	"$match": {"type":"secret"}
},
  {
    "$group": {
      "_id": {
        "rule": "$info.RuleID"
      },
      "count": {
        "$sum": 1
      }
    }
  },
  {
    "$sort": {
      "_id": 1
    }
  },
  {
    "$project": {
      "_id": 0,
      "x": "$_id.rule",
      "y": "$count"
    }
  }
]

    result = list(Findings_collection.aggregate(pipeline))
    print(result)

    return result

@router.get("/download_csv", status_code=status.HTTP_200_OK)
async def secretDownload_csv(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(..., description="Organization name")):
  match_stage = {"org": org}

  pipeline = [
        {"$match": match_stage},
  {
    "$match": {
      "type": "secret"
    }
  },
  {
    "$project": {
			"Created": "$created_timestamp",
      "_id": "$_id",
      "Host": "$host",
      "Url": "$url",
      "Title": "$title",
      "Org": "$org",
      "Description": "$info.description",
      "Severity": "$info.severity",
      "Tool Source": "$tool_source",
      "Falsepositive": "$falsepositive",
			"Rule Id": "$info.RuleID",
			"Key" : "$info.key", 
			"Match" : "$info.Match",
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
    headers={"Content-Disposition": f"attachment; filename=Secert_{org}.csv"}
  )