import json
import logging

from mantis.utils.tool_utils import get_assets_with_non_empty_fields, get_assets_grouped_by_type
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.crud_utils import CrudUtils
from mantis.constants import ASSET_TYPE_SUBDOMAIN
from mantis.utils.common_utils import CommonUtils

class HTTPX_Active(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    
    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = 'echo {subdomain} | httpx -o {output_file_path} -p {ports_comma_seperated} -json'
        self.outfile_extension = ".txt"
        self.assets = await get_assets_with_non_empty_fields(args, "ports")
        self.commands_list = []
        for every_asset in self.assets:  
            domain = every_asset['_id']
            ports = ','.join(str(num) for num in every_asset['ports'][0])
            outfile = CommonUtils.generate_unique_output_file_name(domain, self.outfile_extension)
            command = self.base_command.format(subdomain = domain, output_file_path = outfile, ports_comma_seperated=ports)
            self.commands_list.append((self, command, outfile, domain))
        return self.commands_list
    
    
    def parse_report(self, outfile):
        logging.debug('Parsing HTTPX Report for basic recon - Begins')
        report_dict = []
        tool_output_dict = {}
        with open(outfile) as json_lines:
            for line in json_lines:
                report_dict.append(json.loads(line))
        # for every_asset in report_dict:
        tool_output_dict["active_hosts"] = []
        tool_output_dict["technologies"] = []
        for every_asset in report_dict:
            tool_output_dict["active_hosts"].append(every_asset["url"])
            tool_output_dict["technologies"].extend(every_asset["tech"])
            
        return tool_output_dict


    async def db_operations(self, tool_output_dict, asset):
        await CrudUtils.update_asset(asset=asset, org=self.org, tool_output_dict=tool_output_dict)
