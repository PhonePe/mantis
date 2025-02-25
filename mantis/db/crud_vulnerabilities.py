import logging
from mantis.db.database import findings_collection
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne, InsertOne


async def add_findings_query(findings_data: list) -> None:
    try:
        finding = await findings_collection.insert_many(findings_data, False) # 'ordered': "false"}
        logging.debug(f'Findings inserted')
    except BulkWriteError as bwe:
        logging.debug(f'Findings Bulk write error due to duplicate records')


async def read_findings(pipeline):
    finding_list = []

    try:
        results = findings_collection.aggregate(pipeline)
        for result in await results.to_list(length=None):
            finding_list.append(result)
        return finding_list
    except Exception as e:
        logging.debug(f"Error reading db assets: {e}")

async def findings_bulk_mixed_query(bulk_write_query):

    try:
        result = findings_collection.bulk_write(bulk_write_query)

    except Exception as e:
        logging.debug(f'Findings Bulk write error while update: {e}')

async def check_field_exists(field_name: str, value: str) -> bool:
    try:
        query = {field_name: value}

        result = await findings_collection.find_one(query)

        if result:
            logging.debug(f'Document with {field_name} = {value} exists in the database.')
            return True
        else:
            logging.debug(f'Document with {field_name} = {value} does not exist in the database.')
            return False

    except Exception as e:
        logging.debug(f"Error checking field {field_name} in the database: {e}")
        return False