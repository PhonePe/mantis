import json
import os
import re
import logging
import shutil
import requests

from mantis.utils.crud_utils import CrudUtils
from mantis.config_parsers.config_client import ConfigProvider
class SecretFinder:

    def __init__(self, domain, args, path):
        self.domain = domain
        self.args = args
        try:
            # Create file paths
            self.report_file = os.path.join(path, f'{domain}/report.json')
            self.output_file = os.path.join(path, f'{domain}/output.json')

            # Try reading data from files
            self.report_data = self.read_json_file(self.report_file)
            self.output_data = self.read_json_file(self.output_file)

            logging.debug(f"Report output {self.output_file}")

        except (FileNotFoundError, IOError) as e:
            logging.error(f"Error creating or accessing file: {e}")
            # Optionally handle by setting defaults or skipping file operations
            self.output_file = None
            self.output_data = {}


    def read_json_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        return data


    def extract_filename_from_path(self, file_path):
        return file_path.split('/')[-1]


    def find_matching_urls(self, secrets):
        matching_urls = {}

        for secret in secrets:
            found_urls = []
            for entry in self.output_data:
                if 'url' in entry and secret in entry['url']:
                    found_urls.append(entry['url'])
            if not found_urls:
                for entry in self.report_data:
                    if entry['Secret'] == secret:
                        file_path = entry['File']
                        filename = self.extract_filename_from_path(file_path)
                        regex = re.escape(filename)
                        for entry in self.output_data:
                            if 'url' in entry and re.search(regex, entry['url']):
                                found_urls.append(entry['url'])
            if found_urls:
                matching_urls[secret] = found_urls

        return matching_urls


    async def find_secrets_and_urls(self):
        secrets = self.report_data
        matching_urls = self.find_matching_urls([entry['Secret'] for entry in secrets])
        finding_dict_list = []
        self.finding_type = "secret"
        for secret in secrets:
            urls = matching_urls.get(secret['Secret'], [])
            for url in urls:
                finding_dict = {}
                finding_dict["url"] = url
                if "http" in url:
                    finding_dict["host"] = url.split('/')[2]
                else:
                    finding_dict["host"] = url.split('/')[0]
                finding_dict["title"] = f"Secret Leak"
                finding_dict["org"] = self.args.org
                finding_dict["type"] = "secret"
                finding_dict["info"] = {}
                finding_dict["info"]["key"] = secret['Secret']
                finding_dict["info"]["Match"] = secret['Match']
                finding_dict["info"]["RuleID"] = secret['RuleID']
                finding_dict["info"]["Entropy"] = secret['Entropy']

                finding_dict_list.append(finding_dict)
        if len(finding_dict_list):
            logging.debug("Inserting secrets in db.")
            await CrudUtils.insert_findings(self, None, finding_dict_list, self.finding_type,"host")
        else:
            logging.debug('No secrets found')
        logging.debug("Findings inserted in db")

    async def find_secrets_in_repos(self,github_info):
        secrets = self.report_data
        # TODO change this to make it work with secretfinder also
        if secrets == []:
            return None

        # matching_urls = self.find_matching_urls([entry['Secret'] for entry in secrets])

        passive_assset_list = []
        passive_dict = {}
        passive_dict["asset"] = github_info['Repo Url']
        passive_dict["asset_type"] = "Github"
        passive_dict["org"] = self.args.org
        passive_assset_list.append(passive_dict)

        finding_dict_list = []
        self.finding_type = "secret"
        for secret in secrets:
            finding_dict = {}
            finding_dict["host"] = github_info['Repo Url']
            finding_dict["title"] = f"Github Secret Leak"
            finding_dict["org"] = self.args.org
            finding_dict["type"] = "secret"
            finding_dict["description"] = secret["File"].strip(ConfigProvider.get_config().github_config.download_location)
            finding_dict["info"] = {}
            finding_dict["info"]["key"] = secret['Secret']
            finding_dict["info"]["Match"] = secret['Match']
            finding_dict["info"]["RuleID"] = secret['RuleID']
            finding_dict["info"]["Entropy"] = secret['Entropy']
            finding_dict["info"]["github_source"] = github_info
            finding_dict_list.append(finding_dict)

        if len(finding_dict_list):
            SecretFinder.send_findings_to_webhook(finding_dict)
            logging.info("Inserting secrets in db.")

            await CrudUtils.insert_findings(self, None, finding_dict_list, self.finding_type, "host")
        else:
            logging.info('No secrets found')
        logging.info("Findings inserted in db")
        return True

    @staticmethod
    def send_findings_to_webhook(finding_dict):
        # Format the message for Slack
        slack_message = {
            "text": f"*New Github Secret Leak Found*\n"
                    f"*Host*: {finding_dict['host']}\n"
                    f"*Title*: {finding_dict['title']}\n"
                    f"*Organization*: {finding_dict['org']}\n"
                    f"*Type*: {finding_dict['type']}\n"
                    f"*Description*: {finding_dict['description']}\n"
                    f"*Secret*: {finding_dict['info']['key']}\n"
                    f"*Match*: {finding_dict['info']['Match']}\n"
                    f"*Rule ID*: {finding_dict['info']['RuleID']}\n"
                    f"*Entropy*: {finding_dict['info']['Entropy']}\n"
                    f"*GitHub Source*: {json.dumps(finding_dict['info']['github_source'], indent=2)}"
        }

        headers = {'Content-Type': 'application/json'}

        # Send the POST request to the webhook URL
        webhook_url = "REDACTED"
        response = requests.post(webhook_url, data=json.dumps(slack_message), headers=headers)

        if response.status_code != 200:
            raise ValueError(f"Request to webhook failed with error {response.status_code}: {response.text}")
        else:
            print(f"Successfully sent finding to webhook: {finding_dict}")
