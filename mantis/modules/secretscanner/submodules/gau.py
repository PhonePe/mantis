import os
import logging
from concurrent.futures import ThreadPoolExecutor
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD
from subprocess import Popen
from mantis.config_parsers.config_client import ConfigProvider
import sys



class Gau:
    
    @staticmethod
    def replace_domain_placeholder(command, domain):
        return command.replace('{DOMAIN}', domain)

    @staticmethod
    def run_command(path, domain, command):
        command = command.format(path=path, DOMAIN=domain)
        print(f"Running command '{command}'")
        subprocess_obj = Popen(
                command, stderr=sys.stderr, stdout=sys.stdout, shell=True) 
        code = subprocess_obj.wait()
        output,errors = subprocess_obj.communicate()
        return code, domain, output, errors
    

    @staticmethod
    def create_secret_folder():
        report_output = 'logs/tool_logs/'
        secret_folder = report_output + 'secret'
        if os.path.exists(secret_folder):
            for item in os.listdir(secret_folder):
                item_path = os.path.join(secret_folder, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    Gau.remove_directory(item_path)
        logging.info(f"Creating Secret folder at : {secret_folder}")
        os.makedirs(secret_folder, exist_ok=True)
        return secret_folder

    @staticmethod
    def remove_directory(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                Gau.remove_directory(item_path)
        os.rmdir(directory)

    @staticmethod
    def create_domain_folder(path, domain):
        domain_folder = os.path.join(path, domain)
        if not os.path.exists(domain_folder):
            os.makedirs(domain_folder)

    @staticmethod
    async def process_domains(args):
        
        path = Gau.create_secret_folder()

        domains = await get_assets_grouped_by_type(args, ASSET_TYPE_TLD)
        commands = "gau {DOMAIN} --threads 50 --subs --json --o {path}/{DOMAIN}/{DOMAIN}"
        for domain in domains:
            Gau.create_domain_folder(path, domain)
        
        logging.info("Running Gau...")
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(Gau.run_command, path, domain, commands) for domain in domains]

            # Wait for all tasks to complete
            for future in futures:
                code, domain, output, errors =  future.result()
                if code != 0:
                    logging.error(f"Gau failed for {domain} with code:{code}, errors:{errors}")

        return path       
