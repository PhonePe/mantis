import os
import sys
import yaml
import logging
from mantis.config_parsers.config_models import AppConfig

class ConfigProvider(object):

    yml_config = None

    @staticmethod
    def convert_yml_to_obj(yml_file_path):
        config = dict()
        logging.info(" reading yml file: {}".format(yml_file_path))
        try:
            with open(yml_file_path, 'r') as yml_file:
                yml_to_dict = yaml.load(yml_file, Loader=yaml.SafeLoader)
                config.update(yml_to_dict)
                
                ConfigProvider.yml_config = AppConfig.parse_obj(config)

        except yaml.YAMLError as e:
            logging.error('(convert_yml_to_obj) Error in reading yml file: {}, Reason: {}'.format(yml_file_path, e))
            sys.exit(0)
        except OSError as e:
            logging.error('(convert_yml_to_obj) Error in reading yml file: {}, Reason: {}'.format(yml_file_path, e))
            sys.exit(0)

   
    @staticmethod
    def get_local_config():
        config_path = os.path.join('configs', 'local.yml')
        ConfigProvider.convert_yml_to_obj(config_path)
    

    @staticmethod
    def get_config():
        if ConfigProvider.yml_config:
            return ConfigProvider.yml_config
        else:
            ConfigProvider.get_local_config()
            return ConfigProvider.yml_config

