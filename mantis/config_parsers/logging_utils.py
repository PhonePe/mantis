import os
import logging
import logging.config
from mantis.config_parsers.config_client import ConfigProvider

class LoggingConfig(object):

    @staticmethod    
    def configure_logging():
        log_config = ConfigProvider.get_config().logging
        logging.config.dictConfig(log_config)
        logging.info('MANTIS ASSET DISCOVERY - STARTED') 
