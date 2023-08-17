from mantis.db.crud_assets import read_assets

async def get_active_hosts(org):
    pipeline_hosts_with_ports = [
        {"$match" : {"org" : org}},
        {"$group":  {
            "_id" : "$asset",
            "active_hosts" : { "$push" : "$active_hosts"  }          
            }} 
        ]
    
    assets =  await read_assets(pipeline_hosts_with_ports) 
    if assets:
        return assets
    else: 
        return []

async def get_org_assets(org):
    pipeline_assets_for_org = [
        {"$match" : {"org" : org}}
    ]
    assets =  await read_assets(pipeline_assets_for_org)
    if assets:
        return assets
    else:
        return []

async def get_assets_grouped_by_type(args, asset_type):
    pipeline_type_assets = []
    if args.app:
        pipeline_type_assets.append(
            {"$match" : {"app" : args.app}}
        )
    if args.ignore_stale:
        pipeline_type_assets.append(
            {"$match" : {"stale" : { "$eq": False }}}
        )
    
    pipeline_type_assets.extend([
        {"$match" : {"org" : args.org}},
        {"$match" : {"asset_type" : asset_type}},
        {"$group":  {
            "_id" : None,
            "assets" : { "$push" : "$asset"}
        }}        
    ])
    

    assets = await read_assets(pipeline_type_assets)
    if assets:
        return assets[0]["assets"]
    else:
        return []
    

async def get_assets_with_empty_fields(args, field_name):
    pipeline_empty_fields = []
    if args.app:
        pipeline_empty_fields.append(
            {"$match" : {"org" : args.app}}
            )
        
    if args.ignore_stale:
        pipeline_empty_fields.append(
            {"$match" : {"stale" : { "$eq": False }}}
        )

    pipeline_empty_fields.extend([
        {"$match" : {"org" : args.org}},
        {"$match" : {
            field_name: { "$in": [None, "", []] }
        }},
        {"$group":  {
            "_id" : None,
            "assets" : { "$push" : "$asset"}
            
        }}   
    ])

    assets = await read_assets(pipeline_empty_fields)
    if assets:
        return assets[0]["assets"]
    else:
        return []
    
async def get_assets_with_non_empty_fields(args, field_name):
    pipeline_non_empty_fields = []
    if args.app:
        pipeline_non_empty_fields.append(
            {"$match" : {"org" : args.app}}
            )
        
    if args.ignore_stale:
        pipeline_non_empty_fields.append(
            {"$match" : {"stale" : { "$eq": False }}}
        )
    
    pipeline_non_empty_fields.extend([
        {"$match" : {"org" : args.org}},
        {"$match" : {
            field_name: { "$nin": [None, "", []] }
        }},
        {"$group":  {
            "_id" : "$asset",
            field_name : { "$push" : f"${field_name}" }
        }}   
    ])

    assets = await read_assets(pipeline_non_empty_fields)
    if assets:
        return assets
    else:
        return []
    

async def get_assets_by_field_value(args, field_name, value, asset_type):
    pipeline_assets_by_field_value = []
    if args.app:
        pipeline_assets_by_field_value.append(
            {"$match" : {"org" : args.app}}
            )
        
    pipeline_assets_by_field_value.extend([
        {"$match" : {"org" : args.org}},
        {"$match" : {"asset_type" : asset_type}},
        {"$match" : {
            field_name: value
        }},
        {"$group":  {
            "_id" : 0,
            "assets" : { "$push" : "$asset"}
        }}   
    ])

    assets = await read_assets(pipeline_assets_by_field_value)
    if assets:
        return assets[0]["assets"]
    else:
        return []