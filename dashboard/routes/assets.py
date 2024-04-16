from fastapi import APIRouter, HTTPException, status, Query, Security
from pymongo import MongoClient
import io
import pandas as pd
from fastapi.responses import StreamingResponse
from routes.login_reg import get_current_user
from models.user import User
from typing import Annotated
from config.db import db, Assets_collection, Findings_collection
router = APIRouter(prefix="/assets", tags=["assets"])

# client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.1")


# #mongodb details
# db = client["mantis"]
# Assets_collection = db["assets_collection"]
# Findings_collection = db["findings_collection"]

@router.get("/technologies_q", status_code=200)
async def technologies_q(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$unwind": "$technologies"},
        {"$group": {"_id": "$technologies", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "x": "$_id", "y": "$count"}}
    ]

    result = list(Assets_collection.aggregate(pipeline))

    return result

@router.get("/TotalNetworkAssetCount", status_code=status.HTTP_200_OK)
async def total_network_Asset_Count(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {"asset_type": {"$ne": "certificate"}}

    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
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

@router.get("/TotalTlds", status_code=status.HTTP_200_OK)
async def total_tlds(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])],org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    match_stage["asset_type"] = "TLD"

    pipeline = [
        {"$match": match_stage},
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

@router.get("/TotalSubdomains", status_code=status.HTTP_200_OK)
async def total_subdomains(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    match_stage["asset_type"] = "subdomain"

    pipeline = [
        {"$match": match_stage},
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

@router.get("/TotalIp", status_code=status.HTTP_200_OK)
async def Total_Ip(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    match_stage["asset_type"] = "ip"

    pipeline = [
        {"$match": match_stage},
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

@router.get("/internal_external", status_code=status.HTTP_201_CREATED)
async def internal_external(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": {"$ne": "certificate"}}},
        {"$group": {"_id": {"source": "$source"}, "count": {"$sum": 1}}},
        {"$sort": {"_id.source": 1}},
        {"$project": {"_id": 0, "x": "$_id.source", "y": "$count"}}
    ]

    result = list(Assets_collection.aggregate(pipeline))
    print(result)

    return result

@router.get("/cdn_names_q", status_code=status.HTTP_201_CREATED)
async def cdn_names_q(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$unwind": "$cdn_names"},
        {"$group": {"_id": "$cdn_names", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "x": "$_id", "y": "$count"}}
    ]

    result = list(Assets_collection.aggregate(pipeline))
    print(result)

    return result

@router.get("/waf_q", status_code=status.HTTP_201_CREATED)
async def waf_q(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(None, description="Organization name")):
    match_stage = {}
    if org:
        match_stage["org"] = org

    pipeline = [
        {"$match": match_stage},
        {"$unwind": "$waf"},
        {"$group": {"_id": "$waf", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "x": "$_id", "y": "$count"}}
    ]

    result = list(Assets_collection.aggregate(pipeline))
    print(result)

    return result


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
        {"$match": {"asset_type": {"$ne": "certificate"}}},
        {
            "$project": {
                "_id": False,
                "Asset": "$asset",
                "Type": "$asset_type",
                "App": "$app",
                "Org": "$org",
                "WAF": {"$reduce": {
                    "input": "$waf",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$waf", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "$$this"]},
                            "else": {"$concat": ["$$value", ", ", "$$this"]}
                        }
                    }
                }},
                "Source": "$source",
                "Stale": "$stale",
                "Created": "$created_timestamp",
                "CDN": {"$reduce": {
                    "input": "$cdn_names",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$cdn_names", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "$$this"]},
                            "else": {"$concat": ["$$value", ", ", "$$this"]}
                        }
                    }
                }},
                "Technologies": {"$reduce": {
                    "input": "$technologies",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$technologies", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "$$this"]},
                            "else": {"$concat": ["$$value", ", ", "$$this"]}
                        }
                    }
                }},
                "Webserver": "$webserver",
                "Ports": {"$reduce": {
                    "input": "$ports",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$ports", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "", {"$toLower": "$$this"}]},
                            "else": {"$concat": ["$$value", ", ", {"$toLower": "$$this"}]}
                        }
                    }
                }}
            }
        },
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size}
    ]

    total_records_pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": {"$ne": "certificate"}}},
        {"$group": {"_id": None, "total": {"$sum": 1}}}
    ]
    total_records_result = list(Assets_collection.aggregate(total_records_pipeline))
    total_records = total_records_result[0]["total"] if total_records_result else 0

    result = list(Assets_collection.aggregate(pipeline))

    return {"total_records": total_records, "data": result}


@router.get("/download_csv", status_code=status.HTTP_200_OK)
async def vulnerability_download_csv(current_user: Annotated[User, Security(get_current_user, scopes=["admin", "read","write"])], org: str = Query(..., description="Organization name")):
  match_stage = {"org": org}

  pipeline = [
        {"$match": match_stage},
        {"$match": {"asset_type": {"$ne": "certificate"}}},
        {
            "$project": {
                "_id": False,
                "Asset": "$asset",
                "Type": "$asset_type",
                "App": "$app",
                "Org": "$org",
                "WAF": {"$reduce": {
                    "input": "$waf",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$waf", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "$$this"]},
                            "else": {"$concat": ["$$value", ", ", "$$this"]}
                        }
                    }
                }},
                "Source": "$source",
                "Stale": "$stale",
                "Created": "$created_timestamp",
                "CDN": {"$reduce": {
                    "input": "$cdn_names",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$cdn_names", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "$$this"]},
                            "else": {"$concat": ["$$value", ", ", "$$this"]}
                        }
                    }
                }},
                "Technologies": {"$reduce": {
                    "input": "$technologies",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$technologies", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "$$this"]},
                            "else": {"$concat": ["$$value", ", ", "$$this"]}
                        }
                    }
                }},
                "Webserver": "$webserver",
                "Ports": {"$reduce": {
                    "input": "$ports",
                    "initialValue": "",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$indexOfArray": ["$ports", "$$this"]}, 0]},
                            "then": {"$concat": ["$$value", "", {"$toLower": "$$this"}]},
                            "else": {"$concat": ["$$value", ", ", {"$toLower": "$$this"}]}
                        }
                    }
                }}
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
    headers={"Content-Disposition": f"attachment; filename=Assets_{org}.csv"}
  )