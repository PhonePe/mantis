import json
import logging

from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.crud_utils import CrudUtils
from mantis.constants import ASSET_TYPE_SUBDOMAIN, ASSET_TYPE_IP

class Wafw00f(ToolScanner):

    def __init__(self) -> None:
        super().__init__()


    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = 'wafw00f -a {input_domain} -o {output_file_path} -f json'
        self.outfile_extension = ".json"
        self.assets = await get_assets_grouped_by_type(args, ASSET_TYPE_SUBDOMAIN)
        return super().base_get_commands(self.assets)
    
    
    def parse_report(self, outfile):
        logging.debug('Parsing Wafw00f Report for basic recon - Begins')
        report_dict = {}
        tool_output_dict = {}
        waf_list = []
        with open(outfile) as tool_report:
            report_dict = json.load(tool_report)
        
        for waf in report_dict:
            if 'firewall' in waf:
                if waf['firewall'] != 'None':
                    waf_list.append(waf['firewall'])

        tool_output_dict['waf'] = waf_list

        return tool_output_dict

    async def db_operations(self, tool_output_dict, asset):
        await CrudUtils.update_asset(asset=asset, org=self.org, tool_output_dict=tool_output_dict)
