from mantis.db.crud_assets import read_assets

async def get_orgs():
    pipeline = []

    pipeline.extend([
        {"$group":  {
            "_id" : None, 
            "orgs":{
                "$addToSet": "$org"
                }
            }
        }   
    ])
    orgs = await read_assets(pipeline)

    if orgs:
        return orgs[0]["orgs"]

    else:
        return None