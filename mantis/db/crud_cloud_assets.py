import logging
from pymongo import UpdateOne
from mantis.db.database import cloud_assets_collection


async def upsert_cloud_assets_query(cloud_assets: list) -> int:
    """Upsert cloud resources by _id. Returns number of resources written."""
    if not cloud_assets:
        return 0

    operations = []
    for asset in cloud_assets:
        operations.append(
            UpdateOne(
                {'_id': asset['_id']},
                {'$set': asset},
                upsert=True
            )
        )

    try:
        result = await cloud_assets_collection.bulk_write(operations, ordered=False)
        written = result.upserted_count + result.modified_count
        logging.debug(f'Cloud assets upserted: {written}')
        return written
    except Exception as e:
        logging.error(f'Error upserting cloud assets: {e}')
        return 0


async def deactivate_stale_cloud_assets_query(provider: str, org: str, active_ids: list, timestamp: str, account_id: str = None) -> int:
    """Mark cloud resources (for a provider+org, optionally scoped to one account)
    not seen in the latest sync as inactive.

    `active_ids` are the _id values collected in the current run. Returns the
    number of resources newly marked inactive.
    """
    if not active_ids:
        # Guard against silent/empty syncs deactivating the entire inventory.
        logging.warning(f'No active ids for {provider}/{org}; skipping stale deactivation')
        return 0

    query = {
        'provider': provider,
        'org': org,
        'is_active': True,
        '_id': {'$nin': active_ids},
    }
    if account_id:
        query['account_id'] = account_id
    try:
        result = await cloud_assets_collection.update_many(
            query,
            {'$set': {'is_active': False, 'updated_timestamp': timestamp}}
        )
        if result.modified_count:
            logging.info(f'Marked {result.modified_count} stale {provider} resource(s) inactive for {org}')
        return result.modified_count
    except Exception as e:
        logging.error(f'Error deactivating stale cloud assets: {e}')
        return 0


async def read_cloud_assets(query: dict) -> list:
    """Read cloud resources matching a Mongo filter query."""
    cloud_assets = []
    try:
        cursor = cloud_assets_collection.find(query)
        for result in await cursor.to_list(length=None):
            cloud_assets.append(result)
    except Exception as e:
        logging.error(f'Error reading cloud assets from DB: {e}')
    return cloud_assets


async def delete_cloud_assets_query(query: dict) -> int:
    """Delete cloud resources matching a Mongo filter query. Returns deleted count."""
    try:
        if not query:
            return 0
        result = await cloud_assets_collection.delete_many(query)
        logging.info(f"Deleted {result.deleted_count} cloud asset(s) from the database")
        return result.deleted_count
    except Exception as e:
        logging.error(f'Error deleting cloud assets: {e}')
        return 0
