import json
import mantis.constants as constants
from mantis.utils.crud_utils import CrudUtils
from mantis.models.args_model import ArgsModel
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.utils.common_utils import CommonUtils
from mantis.utils.tool_utils import get_assets_by_field_value, get_assets_with_non_empty_fields

'''
Corsy is used to find CORS misconfiguration for a provided subdomain
Note: Only the domains resolving to an IP are taken into account
Output: JSON file
'''

class Corsy(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = 'python3 /usr/bin/Corsy/corsy.py -u {input_domain} -o {output_file_path} -d 1'
        self.outfile_extension = ".json"
        self.commands_list = []
        self.assets = await get_assets_with_non_empty_fields(self, args, "active_hosts")
        for every_asset in self.assets:
            if "_id" in every_asset:
                domain = every_asset["_id"]
                for active_hosts in every_asset["active_hosts"][0]:
                    outfile = CommonUtils.generate_unique_output_file_name(domain, self.outfile_extension)
                    command = self.base_command.format(input_domain = active_hosts, output_file_path = outfile)
                    self.commands_list.append((self, command, outfile, domain))
        return self.commands_list

    def parse_report(self, outfile):
        report_dict = []
        report_list = []
        self.finding_type = "vulnerability"
        # Convert json file to dict
        # Give try catch block here, since file will not be present if no vulnerability is found
        with open(outfile) as report_out:
            report_dict = json.load(report_out)

        if report_dict:
            for key, value in report_dict.items():

                finding_dict = {}
                finding_dict["title"] = f"CORS Misconfiguration - {value.get('class')}"
                finding_dict["type"] = "vulnerability"
                finding_dict["url"] = key
                finding_dict["description"] = value.get('description') + value.get('exploitation')
                finding_dict["severity"] = value.get('severity')
                finding_dict["remediation"] = "https://portswigger.net/web-security/cors#how-to-prevent-cors-based-attacks"
                finding_dict["others"] = {}
                finding_dict["others"]["acao_header"] = value.get('acao header')
                finding_dict["others"]["acac_header"] = value.get('acac header')
                finding_dict["org"] = self.org
    
                report_list.append(finding_dict)
                    
            return report_list
        
    async def db_operations(self, output_dict, asset):
        await CrudUtils.insert_findings(self, asset, output_dict, self.finding_type)
