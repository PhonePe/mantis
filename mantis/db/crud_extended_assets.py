import logging
from pymongo.errors import BulkWriteError
from mantis.db.database import extended_assets_collection

async def add_extended_assets_query(asset_data: list) -> None:
    try:
        asset = await extended_assets_collection.insert_many(asset_data, False) # 'ordered': "false"}
        logging.debug(f'Assets inserted')
    except BulkWriteError as bwe:
        #logging.warning(f'Bulk write error due to duplicate records - {bwe.details}')
        logging.debug(f'Assets Bulk write error due to duplicate records')


async def read_extended_assets(pipeline):
    asset_list = []
    results = extended_assets_collection.aggregate(pipeline)
    for result in await results.to_list(length=None):
        asset_list.append(result)
    return asset_list

async def read_extended(pipeline):
    passive_list = []

    try:
        results = extended_assets_collection.aggregate(pipeline)
        for result in await results.to_list(length=None):
            passive_list.append(result)
        return passive_list
    except Exception as e:
        logging.debug(f"Error reading passive assets from DB: {e}")
        return []

async def findings_bulk_mixed_query(bulk_write_query):

    try:
        result = extended_assets_collection.bulk_write(bulk_write_query)

    except Exception as e:
        logging.debug(f'Findings Bulk write error while update: {e}')

async def update_extended_asset_query(asset: str, org: str, mongodb_query):

    asset_exists =  await extended_assets_collection.find_one({'_id': asset, 'org': org})
    if asset_exists:
        updated_asset = await extended_assets_collection.update_one(
            {'_id': asset, 'org': org},
            mongodb_query,
            True
        )
        if updated_asset:
            return True
        return False
    else:
        logging.error(f'Asset {asset} does not exists in DB, Update failed')
