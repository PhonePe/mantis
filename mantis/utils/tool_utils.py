from mantis.db.crud_assets import read_assets
from mantis.db.crud_vulnerabilities import read_findings
from mantis.db.crud_extended_assets import read_extended_assets
from mantis.utils.config_utils import ConfigUtils
from datetime import datetime


async def get_active_hosts(org):
    pipeline_hosts_with_ports = [
        {"$match": {"org": org}},
        {"$group": {
            "_id": "$asset",
            "active_hosts": {"$push": "$active_hosts"}
        }}
    ]

    assets = await read_assets(pipeline_hosts_with_ports)
    if assets:
        return assets
    else:
        return []


async def get_org_assets(org):
    pipeline_assets_for_org = [
        {"$match": {"org": org}}
    ]
    assets = await read_assets(pipeline_assets_for_org)
    if assets:
        return assets
    else:
        return []


async def get_assets_grouped_by_type(self, args, asset_type):
    pipeline_type_assets = []

    pipeline_type_assets.extend(get_pipeline(self=self, args=args))

    pipeline_type_assets.extend([
        {"$match": {"org": args.org}},
        {"$match": {"asset_type": asset_type}},
        {"$group": {
            "_id": None,
            "assets": {"$push": "$asset"}
        }}
    ])

    assets = await read_assets(pipeline_type_assets)
    if assets:
        return assets[0]["assets"]
    else:
        return []


async def get_assets_with_empty_fields(self, args, field_name):
    pipeline_empty_fields = []

    pipeline_empty_fields.extend(get_pipeline(self=self, args=args))

    pipeline_empty_fields.extend([
        {"$match": {"org": args.org}},
        {"$match": {
            field_name: {"$in": [None, "", []]}
        }},
        {"$group": {
            "_id": None,
            "asset": {"$push": "$asset"}

        }}
    ])

    assets = await read_assets(pipeline_empty_fields)
    if assets:
        return assets[0]["asset"]
    else:
        return []


async def get_assets_with_non_empty_fields(self, args, field_name):
    pipeline_non_empty_fields = []

    pipeline_non_empty_fields.extend(get_pipeline(self=self, args=args))

    pipeline_non_empty_fields.extend([
        {"$match": {"org": args.org}},
        {"$match": {
            "asset_type": {"$nin": ["certificate"]}
        }},
        {"$match": {
            field_name: {"$nin": [None, "", []]}
        }},
        {"$group": {
            "_id": "$asset",
            field_name: {"$push": f"${field_name}"}
        }}
    ])

    assets = await read_assets(pipeline_non_empty_fields)
    if assets:
        return assets
    else:
        return []


async def get_assets_by_field_value(self, args, field_name, value, asset_type):
    pipeline_assets_by_field_value = []

    pipeline_assets_by_field_value.extend(get_pipeline(self=self, args=args))

    pipeline_assets_by_field_value.extend([
        {"$match": {"org": args.org}},
        {"$match": {"asset_type": asset_type}},
        {"$match": {
            field_name: value
        }},
        {"$group": {
            "_id": 0,
            "assets": {"$push": "$asset"}
        }}
    ])

    assets = await read_assets(pipeline_assets_by_field_value)
    if assets:
        return assets[0]["assets"]
    else:
        return []


def get_pipeline(self, args):
    pipeline = []
    if args.app:
        pipeline.append(
            {"$match": {"org": args.app}}
        )

    if args.ignore_stale:
        pipeline.append(
            {"$match": {"stale": {"$eq": False}}}
        )
    if self is not None:
        if ConfigUtils.is_scanNewOnly_tool(type(self).__name__, args):
            pipeline.append(
                {"$match": {"created_timestamp": {"$gte": datetime.today().strftime('%Y-%m-%d')}}}

            )
    if args.subdomain:
        pipeline.append(
            {"$match": {"asset": args.subdomain}}
        )

    return pipeline


async def get_findings_by_asset(asset, finding_type):
    pipeline = []

    pipeline.extend([
        {"$match": {"host": asset}},
        {"$match": {"type": finding_type}},

        {"$group": {
            "_id": "$_id",
            "title": {"$push": "$title"}
        }}
    ])
    findings = await read_findings(pipeline)

    if findings:

        return findings
    else:
        return []


async def get_extended_by_asset(asset: str, asset_type: str = None):
    pipeline = []

    # Match the asset in the Passive collection
    pipeline.append({"$match": {"asset": asset}})

    # Optionally match the asset type if provided
    if asset_type:
        pipeline.append({"$match": {"asset_type": asset_type}})

    # Group by _id and push relevant fields (e.g., asset_type, org)
    pipeline.append({
        "$group": {
            "_id": "$_id",
            "asset_type": {"$first": "$asset_type"},
            "org": {"$first": "$org"},
            "availability_status": {"$first": "$availability_status"},
        }
    })

    passives = await read_extended_assets(pipeline)

    return passives if passives else []


async def get_secret_by_url(args, url):
    pipeline_type_assets = []

    pipeline_type_assets.extend([
        {"$match": {"org": args.org}},
        {"$match": {"type": url}},
        {"$group": {
            "_id": None,
            "urls": {"$push": "$url"}
        }}
    ])

    assets = await read_findings(pipeline_type_assets)
    if assets:
        return assets[0]["url"]
    else:
        return []