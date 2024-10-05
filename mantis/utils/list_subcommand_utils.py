import logging
from mantis.db.crud_assets import read_assets


async def get_orgs():
    pipeline = []

    pipeline.extend([{"$group": {"_id": None, "orgs": {"$addToSet": "$org"}}}])
    orgs = await read_assets(pipeline)

    if orgs:
        return orgs[0]["orgs"]

    else:
        return None


async def get_domains(orgs:list[str], asset_types:list[str], after_filter:str, before_filter:str):
    if len(orgs) == 0:
        logging.warning('No orgs selected')
        return []

    if len(asset_types) == 0:
        logging.warning('no asset type was selected')
        return []
    
    match_filter = {
        "org": {"$in": orgs},
        "asset_type": {"$in": asset_types},
    }

    if after_filter:
        match_filter.setdefault("created_timestamp", {})
        match_filter["created_timestamp"]["$gte"] = after_filter

    if before_filter:
        match_filter.setdefault("created_timestamp", {})
        match_filter["created_timestamp"]["$lte"] = before_filter

    pipeline = [
        {
            "$match": match_filter
        },
        {
            "$group": {
                "_id": None,
                "asset": {"$addToSet": "$asset"},
            },
        },
    ]

    result = await read_assets(pipeline)
    domains = []
    if result and len(result) > 0:
        domains = result[0].get('asset', [])
    else:
        logging.warning('No match found')
    return domains
