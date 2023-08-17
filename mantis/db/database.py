from mantis.config_parsers.config_client import ConfigProvider
import motor.motor_asyncio

mongo_db_connction = ConfigProvider.get_config().dbConfig.mongoConnectionString
client = motor.motor_asyncio.AsyncIOMotorClient(mongo_db_connction)

database = client.mantis

assets_collection = database.get_collection("assets_collection")
findings_collection = database.get_collection("findings_collection")
