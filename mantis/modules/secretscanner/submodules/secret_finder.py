import json
import os
import re
import logging
from mantis.utils.crud_utils import CrudUtils

class SecretFinder:

    def __init__(self, domain, args, path):
        self.domain = domain
        self.args = args
        self.report_file = os.path.join(path,f'{domain}/report.json')
        self.output_file = os.path.join(path,f'{domain}/output.json')
        self.report_data = self.read_json_file(self.report_file)
        self.output_data = self.read_json_file(self.output_file)
        logging.debug(f"Report output {self.output_file }")


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
