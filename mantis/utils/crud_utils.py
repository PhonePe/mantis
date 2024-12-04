import hashlib
import logging
from mantis.db.db_models import Assets, Findings, Extended
from mantis.db.crud_assets import add_assets_query, update_asset_query
from mantis.db.crud_extended_assets import add_extended_assets_query
from mantis.db.crud_vulnerabilities import add_findings_query, findings_bulk_mixed_query
from mantis.utils.common_utils import CommonUtils
from mantis.config_parsers.config_client import ConfigProvider
from mantis.constants import ASSET_TYPE_SUBDOMAIN
from mantis.utils.tool_utils import get_findings_by_asset
from pymongo import UpdateOne, InsertOne
from pydantic import ValidationError
from datetime import datetime
import time


# These function takes the input as the list of dict that are parsed into
# the pydantic object and returned as list of dict
class CrudUtils:

    @staticmethod
    def validate_assets(assets: list, source):
        # print("asset_list:::: ", assets)
        assets_list = []
        try:
            # TODO Can we parallelize this. Time complexity is O(N).
            if assets:
                for asset in assets:
                    if asset["asset_type"] == ASSET_TYPE_SUBDOMAIN:
                        asset['app'] = CrudUtils.assign_app_context(asset['asset'])
                    validated_asset_dict = Assets(**asset).dict()
                    validated_asset_dict['_id'] = validated_asset_dict['asset']
                    validated_asset_dict['source'] = source
                    validated_asset_dict['created_timestamp'] = CommonUtils.get_ikaros_std_timestamp()
                    assets_list.append(validated_asset_dict)
        except Exception as e:
            logging.error(f"Error parsing asset list {e}")
        return assets_list

    @staticmethod
    def validate_findings(obj, asset: str, findings: list, app_context_param):
        findings_list = []
        new_findings_ids = []
        try:
            if findings:
                for finding in findings:
                    if asset is not None:
                        finding["host"] = asset
                    finding["tool_source"] = type(obj).__name__
                    finding["created_timestamp"] = CommonUtils.get_ikaros_std_timestamp()
                    if asset is not None:
                        finding['app'] = CrudUtils.assign_app_context(asset)
                    else:
                        finding['app'] = CrudUtils.assign_app_context(finding[app_context_param])

                    single_finding = Findings.parse_obj(finding).dict()
                    single_finding["_id"] = CrudUtils.generate_unique_hash(
                        single_finding["host"],
                        single_finding["title"],
                        single_finding["type"],
                        single_finding["tool_source"],
                        single_finding["url"],
                        single_finding["info"],
                        single_finding["others"]
                    )
                    findings_list.append(single_finding)
                    new_findings_ids.append(single_finding["_id"])
        except Exception as e:
            logging.error(f"Error parsing asset list {e}")
        return findings_list, new_findings_ids


    @staticmethod
    def validate_extended_assets(assets: list, source):
        # print("asset_list:::: ", assets)
        assets_list = []
        try:
            if assets:
                for asset in assets:
                    validated_asset_dict = Extended(**asset).dict()
                    validated_asset_dict['_id'] = asset['_id']
                    validated_asset_dict['asset'] = asset['asset']
                    validated_asset_dict['url'] = asset['url']
                    validated_asset_dict['asset_type'] = asset['asset_type']
                    validated_asset_dict['org'] = asset['org']
                    validated_asset_dict['created_timestamp'] = CommonUtils.get_ikaros_std_timestamp()
                    assets_list.append(validated_asset_dict)
        except Exception as e:
            logging.error(f"Error parsing asset list {e}")
        return assets_list


    ## This function validates the dict against the pydantic and inserts the dict in the database.
    @staticmethod
    async def insert_assets(assets: list, source='external'):
        asset_list = CrudUtils.validate_assets(assets=assets, source=source)
        if asset_list:
            await add_assets_query(asset_data=asset_list)

    async def update_asset(asset: str, org: str, tool_output_dict: dict):
        logging.debug(f"Asset {asset} getting updated for org {org}")
        mongodb_query = {}

        for key in tool_output_dict:
            if key in Assets.__fields__:
                key_dict = {}
                if isinstance(tool_output_dict[key], list):
                    if "$addToSet" not in mongodb_query:
                        mongodb_query["$addToSet"] = {}
                    key_dict[key] = {'$each': list(tool_output_dict[key])}

                    mongodb_query["$addToSet"].update(key_dict)
                else:
                    if "$set" not in mongodb_query:
                        mongodb_query["$set"] = {}
                    key_dict[key] = tool_output_dict[key]
                    mongodb_query["$set"].update(key_dict)

            else:
                logging.warning(f"{key} does not exist in database model. This key will be ignored")

        if "$set" in mongodb_query:
            updated_timestamp = {"updated_timestamp": CommonUtils.get_ikaros_std_timestamp(),
                                 "app": CrudUtils.assign_app_context(asset)}
            mongodb_query["$set"].update(updated_timestamp)
        elif "$addToSet" in mongodb_query:
            updated_timestamp = {"updated_timestamp": CommonUtils.get_ikaros_std_timestamp(),
                                 "app": CrudUtils.assign_app_context(asset)}
            mongodb_query["$set"] = updated_timestamp

        logging.debug(f"Updated tool dict  {mongodb_query}")
        if ("$addToSet" in mongodb_query and len(mongodb_query["$addToSet"])) or (
                "$set" in mongodb_query and len(mongodb_query["$set"])):
            await update_asset_query(asset=asset, org=org, mongodb_query=mongodb_query)
        else:
            logging.debug("No output generated by tool or incorrect keys passed")

    @staticmethod
    async def insert_findings(obj, asset: str, findings: list, finding_type, app_context_param=None, ):
        findings_list, new_finding_ids = CrudUtils.validate_findings(obj, asset, findings=findings,
                                                                     app_context_param=app_context_param)

        bulk_write_query = []
        ## close reopen insert
        db_findings = await get_findings_by_asset(asset, finding_type)
        logging.debug("New finding IDS ", new_finding_ids, len(new_finding_ids))
        logging.debug("Asset Name: ", asset)
        logging.debug("findings list: ", findings_list, len(findings_list))
        logging.debug("DB findings ", db_findings, len(db_findings))
        # time.sleep(10)
        try:
            for db_finding in db_findings:
                if db_finding["_id"] not in new_finding_ids:

                    bulk_write_query.append(UpdateOne({"_id": db_finding["_id"]},
                                                      {"$set":
                                                           {"updated_timestamp": CommonUtils.get_ikaros_std_timestamp(),
                                                            "status": "Fixed"
                                                            }
                                                       }, upsert=True))
                    logging.debug("Bulk write query ", bulk_write_query)
                elif db_finding["_id"] in new_finding_ids:

                    bulk_write_query.append(UpdateOne({"_id": db_finding["_id"]},
                                                      {"$set":
                                                           {"updated_timestamp": CommonUtils.get_ikaros_std_timestamp(),
                                                            "status": "Open"
                                                            }
                                                       }, upsert=True))

                    logging.debug("Bulk write query ", bulk_write_query)
        except Exception as e:
            logging.error(f"Exception occured while inserting findings {e}")
            exit(1)

        await findings_bulk_mixed_query(bulk_write_query)

        await add_findings_query(findings_data=findings_list)

    @staticmethod
    async def insert_extended_assets(assets: list, source='external'):
        asset_list = CrudUtils.validate_extended_assets(assets=assets, source=source)
        if asset_list:
            await add_extended_assets_query(asset_data=asset_list)

    @staticmethod
    def create_assets_dict(args, assets_with_type: list):
        asset_dict_list = []
        for asset in assets_with_type:
            if 'asset' in asset and 'type' in asset and 'org' in asset:
                asset_dict = {}
                asset_dict['_id'] = asset['asset']
                asset_dict['asset'] = asset['asset']
                asset_dict['asset_type'] = asset['type']
                asset_dict['org'] = asset['org']
                asset_dict['created_timestamp'] = CommonUtils.get_ikaros_std_timestamp()

                if args.stale:
                    asset_dict['stale'] = True
                else:
                    asset_dict['stale'] = False

                asset_dict_list.append(asset_dict)

        return asset_dict_list

    @staticmethod
    def get_TLD_assets(asset_dict) -> list:
        for keys in asset_dict:
            if keys['_id'] == 'TLD':
                return keys['assets']

    @staticmethod
    def get_subdomain_assets(asset_dict) -> list:
        for keys in asset_dict:
            if keys['_id'] == 'subdomain':
                return keys['assets']

    @staticmethod
    def get_ip_assets(asset_dict) -> list:
        for keys in asset_dict:
            if keys['_id'] == 'ip':
                return keys['assets']

    @staticmethod
    def generate_unique_hash(host, title, type, tool_source, url, info, others):
        # Generate a hash using the params to avoid duplicates
        hash = hashlib.md5(
            str(host).encode() + str(title).encode() + str(type).encode() + str(tool_source).encode() + str(
                url).encode()
            + str(info).encode() + str(others).encode())
        return hash.hexdigest()

    @staticmethod
    def assign_app_context(domain):
        app_context_dict = ConfigProvider.get_config().app
        default = app_context_dict["default"]
        for key, values in app_context_dict.items():
            # print(key, values)
            for value in values:
                if value in domain:
                    return key
        return default[0]
