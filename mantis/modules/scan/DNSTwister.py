import logging
import json
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
        self.assets = await get_assets_by_field_value(args, "stale", False, constants.ASSET_TYPE_TLD)
        db_assets_dict = await get_assets_with_non_empty_fields(args, "asset")
        self.db_assets = []
        for asset in db_assets_dict:
            self.db_assets.extend(asset['asset'])
        return super().base_get_commands(self.assets)

    def parse_report(self, outfile):
        report_dict = []
        report_list = []
        # Convert json lines file to dict
        with open(outfile) as report_out:
            report_dict = json.load(report_out)
        if report_dict:
            for phishing_domain in report_dict:

                if "fuzzer" in phishing_domain and phishing_domain['fuzzer'] != constants.DNS_TWISTER_FUZZER_ORIGINAL:
                    finding_dict = {}
                    finding_dict["title"] = f"Phishing Domain - {phishing_domain['domain']}"
                    finding_dict["type"] = constants.FINDING_TYPE_PHISHING
                    finding_dict["url"] = phishing_domain['domain']
                    finding_dict["severity"] = constants.HIGH_SEVERITY
                    finding_dict["remediation"] = "Inform Anti-Phishing team and take appropriate action"
                    finding_dict["others"] = {}
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
    
    async def db_operations(self, output_dict, asset):
        await CrudUtils.insert_findings(self, asset, output_dict)
