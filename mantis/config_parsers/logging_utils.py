import os
import logging
import logging.config
from mantis.models.args_model import ArgsModel
from mantis.config_parsers.config_client import ConfigProvider

class LoggingConfig(object):

    @staticmethod    
    def configure_logging(args: ArgsModel):
        if args.verbose:
            log_config = ConfigProvider.get_config().logging_debug
            logging.config.dictConfig(log_config)
            logging.info('MANTIS ASSET DISCOVERY - STARTED') 
            logging.info("Debug mode enabled")
        else:
            log_config = ConfigProvider.get_config().logging
            logging.config.dictConfig(log_config)
            logging.info('MANTIS ASSET DISCOVERY - STARTED') 
