import logging
from mantis.db.database import findings_collection
from pymongo.errors import BulkWriteError


async def add_findings_query(findings_data: list) -> None:
    try:
        finding = await findings_collection.insert_many(findings_data, False) # 'ordered': "false"}
        logging.info(f'Findings inserted')
    except BulkWriteError as bwe:
        logging.warning(f'Findings Bulk write error due to duplicate records')


async def read_findings(pipeline):
    asset_list = []
    results = findings_collection.aggregate(pipeline)
    for result in await results.to_list(length=None):
        asset_list.append(result)
    return asset_list
