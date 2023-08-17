import os
import pytz
import uuid
import logging
import datetime
from mantis.config_parsers.config_client import ConfigProvider

class CommonUtils:

    @staticmethod
    def parse_file(file_name: str) -> list:
        logging.debug(f"file_process() {file_name}")
        try:
            with open(file_name) as file:
                hosts = [line.rstrip() for line in file]
                hosts = [line for line in hosts if line]
                return hosts
        except FileNotFoundError:
            logging.error(f"Input file {file_name} is not found, QUTTING !")
            exit(1)

    @staticmethod
    def get_ikaros_std_timestamp():
        ist =  pytz.timezone('Asia/Kolkata')
        return datetime.datetime.now(ist).isoformat()

    @staticmethod
    def strip_url_scheme(target):
        target=target.replace('http://','')
        target=target.replace('https://','')
        if target[-1] == "/":
            target = target[:-1]
        logging.debug(f"Post strip_chars {target}")
        return target

    @staticmethod
    def generate_unique_output_file_name(domain, extension):
        outputDir = 'logs/tool_logs/'
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        outfile = outputDir + str(uuid.uuid4()) + extension
        return outfile
    