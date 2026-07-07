import logging
from mantis.db.crud_assets import delete_assets_query
from mantis.db.crud_extended_assets import delete_extended_assets_query
from mantis.db.crud_vulnerabilities import delete_findings_query
    
async def deboard_organisation(args):
    try:
        org = args.org
        subdomain = args.subdomain
        collections = args.collections or ["assets", "findings", "extended_assets"]

        logging.info(f"Target collections for deboard process: {', '.join(collections)}")

        base_query = {"org": org}
        queries = {
            "assets": base_query.copy(),
            "findings": base_query.copy(),
            "extended_assets": base_query.copy(),
        }

        if subdomain:
            queries["assets"]["asset"] = subdomain
            queries["findings"]["host"] = subdomain
            queries["extended_assets"]["asset"] = subdomain

        delete_methods = {
            "assets": delete_assets_query,
            "findings": delete_findings_query,
            "extended_assets": delete_extended_assets_query,
        }

        deletion_results = {}

        for collection in collections:
            if collection in delete_methods:
                deletion_results[collection] = await delete_methods[collection](queries[collection])

        if not any(deletion_results.values()):
            return False

        return True

    except Exception as e:
        logging.error(f"Error deboarding organisation {org}: {e}")
        return False
