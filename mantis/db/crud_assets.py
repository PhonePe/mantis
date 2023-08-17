import logging
from pymongo.errors import BulkWriteError
from mantis.db.database import assets_collection

async def add_assets_query(asset_data: list) -> None:
    try:
        logging.debug(f"Assets in add_assets_query: {asset_data}")
        asset = await assets_collection.insert_many(asset_data, False) # 'ordered': "false"}
        logging.info(f'Assets inserted')
    except BulkWriteError as bwe:
        #logging.warning(f'Bulk write error due to duplicate records - {bwe.details}')
        logging.warning(f'Assets Bulk write error due to duplicate records')


async def read_assets(pipeline):
    asset_list = []
    results = assets_collection.aggregate(pipeline)
    for result in await results.to_list(length=None):
        asset_list.append(result)
    return asset_list


async def update_asset_query(asset: str, org: str, mongodb_query):

    asset_exists =  await assets_collection.find_one({'_id': asset, 'org': org})
    if asset_exists: 
        updated_asset = await assets_collection.update_one(
            {'_id': asset, 'org': org},
            mongodb_query,
            True
        )
        if updated_asset:
            return True
        return False
    else:
        logging.error(f'Asset {asset} does not exists in DB, Update failed')
