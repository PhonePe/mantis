import json
import logging
import requests
import mantis.constants as constants
from mantis.utils.crud_utils import CrudUtils
from mantis.models.args_model import ArgsModel
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.utils.tool_utils import get_assets_by_field_value, get_assets_with_non_empty_fields

'''
DNS Twister Module is used to find the phishing domains for a given TLD. 
Note: Only the domains resolving to an IP are taken into account
Output: JSON file
Information inserted into DB:
- Phishing domain
- Fuzzer

This also checks the discovered domains against the inserted stale domains by the org. 
'''

class DNSTwister(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = 'dnstwist {input_domain} -r -o {output_file_path} -f json'
        self.outfile_extension = ".json"
        self.assets = await get_assets_by_field_value(self, args, "stale", False, constants.ASSET_TYPE_TLD)
        db_assets_dict = await get_assets_with_non_empty_fields(self, args, "asset")
        self.db_assets = []
        # print("self base command::: ", self.base_command)
        for asset in db_assets_dict:
            self.db_assets.extend(asset['asset'])
        return super().base_get_commands(self.assets)

    def parse_report(self, outfile):
        report_dict = []
        report_list = []
        session = requests.Session()
        session.max_redirects = 3
        self.finding_type = constants.FINDING_TYPE_PHISHING
        # Convert json lines file to dict
        with open(outfile) as report_out:
            report_dict = json.load(report_out)
        try:
            if report_dict:
                stopwords_search_list = ["buy this domain", "get this domain", "This domain is for sale", "purchase this domain"]
                for phishing_domain in report_dict:

                    if "fuzzer" in phishing_domain and phishing_domain['fuzzer'] != constants.DNS_TWISTER_FUZZER_ORIGINAL:
                        finding_dict = {}
                        finding_dict["url"] = phishing_domain['domain']
                        finding_dict["others"] = {}
                        try:
                            # print("phishing_domain['domain']", phishing_domain['domain'])
                            if finding_dict["url"] not in self.db_assets:
                                phishing_domain_response = session.get('http://'+phishing_domain['domain'])
                            # print("response", phishing_domain_response.status_code)
                                if phishing_domain_response.status_code in [200, 302, 301]:
                                    
                                    for string in stopwords_search_list:
                                        if string in phishing_domain_response.text:
                                            finding_dict["others"]["probability"] = "Low probable"
                                            finding_dict["falsepositive"] = True
                                            
                                    for tld in self.assets:
                                        if tld in phishing_domain_response.text:
                                            finding_dict["others"]["probability"] = "More probable"
                                else:
                                    finding_dict["falsepositive"] = True
                                    finding_dict["others"]["status_code"] = phishing_domain_response.status_code
                            else:
                                finding_dict["falsepositive"] = True

                        except requests.TooManyRedirects:
                            finding_dict["others"]["probability"] = "Too Many redirects"
                            finding_dict["falsepositive"] = True
                        except Exception as e:
                            pass
                        # print(phishing_domain_response.status_code, "Status code")
                        finding_dict["title"] = f"Phishing Domain - {phishing_domain['domain']}"
                        finding_dict["type"] = constants.FINDING_TYPE_PHISHING
                        
                        finding_dict["severity"] = constants.HIGH_SEVERITY
                        finding_dict["remediation"] = "Inform Anti-Phishing team and take appropriate action"
                        
                        finding_dict["others"]["fuzzer"] = phishing_domain["fuzzer"]
                        finding_dict["org"] = self.org
                        if finding_dict["url"] in self.db_assets:
                            finding_dict["falsepositive"] = True
                        else:
                            finding_dict["falsepositive"] = False
                        report_list.append(finding_dict)
                        
                return report_list
            else:
                logging.warning('DNSTwister output file found, but no vulnerabilities were reported')
        except Exception as e:
            print(e)
            
    async def db_operations(self, output_dict, asset):
        await CrudUtils.insert_findings(self, asset, output_dict, self.finding_type)
