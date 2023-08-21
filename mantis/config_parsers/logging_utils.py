import os
import logging
import logging.config
from mantis.models.args_model import ArgsModel
from mantis.config_parsers.config_client import ConfigProvider

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] --> %(filename)s: %(lineno)d - %(levelname)s: %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    

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
            logging.StreamHandler().setFormatter(CustomFormatter())
            logging.info('MANTIS ASSET DISCOVERY - STARTED') 
