import os
import yaml
import logging
from concurrent.futures import ThreadPoolExecutor
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD

class GitleaksRunner:

    @staticmethod
    def run_command(domain, command, path):
        command = command.format(path=path, DOMAIN=domain)
        logging.debug(f"Running command '{command}'")
        os.system(command)

    @staticmethod
    async def process_domains(args, path):

        domains = await get_assets_grouped_by_type(None, args, ASSET_TYPE_TLD)
        commands = "gitleaks detect --source {path}/{DOMAIN}/ --no-git -f json -r {path}/{DOMAIN}/report.json -l trace -v"
        logging.debug("Running GitLeaks...")
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(GitleaksRunner.run_command, domain, commands, path) for domain in domains ]
            # Wait for all tasks to complete
            for future in futures:
                future.result()
    @staticmethod
    def process_repos(domain,path):
        commands = "gitleaks detect --source {path}{DOMAIN}/ --no-git -f json -r {path}{DOMAIN}/report.json -l trace -v"
        logging.debug("Running GitLeaks...")
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(GitleaksRunner.run_command, domain, commands, path) ]
            # Wait for all tasks to complete
            for future in futures:
                future.result()