import json
import logging
from mantis.models.args_model import ArgsModel
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_SUBDOMAIN, ASSET_TYPE_IP
from mantis.utils.crud_utils import CrudUtils

'''
Naabu Module is used in discovering ports
Scan types supported: Passive and Active
Output: JSON file
Information inserted into DB:
- ports
'''
class Naabu(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        if args.passive:
            self.base_command = 'naabu -host {input_domain} -json -o {output_file_path} --passive'
        else:
            self.base_command = 'naabu -scan-all-ips -scan-type s -Pn -rev-ptr -warm-up-time 0 -host {input_domain} -json -o {output_file_path}'
        self.outfile_extension = ".json"
        self.assets = await get_assets_grouped_by_type(args, ASSET_TYPE_SUBDOMAIN)
        self.assets.extend(await get_assets_grouped_by_type(args, ASSET_TYPE_IP))
        
        return super().base_get_commands(self.assets)
    
    def parse_report(self, outfile):
        naabu_output_dict = []
        tool_output_dict = {}
        hosts = []
        
        with open(outfile) as json_lines:
            for line in json_lines:
                naabu_output_dict.append(json.loads(line))
    

        for every_host in naabu_output_dict:
            hosts.append(every_host['host'])
        hosts = list(set(hosts))
        # Get ports list for every unique hosts
        for every_host in hosts:
            ports = []
            
            for every_dict in naabu_output_dict:
                if every_dict['host'] == every_host:
                    ports.append(every_dict['port']["Port"])
            tool_output_dict['ports'] = ports
        
        return tool_output_dict
    
    async def db_operations(self, tool_output_dict, asset):
        await CrudUtils.update_asset(asset=asset, org=self.org, tool_output_dict=tool_output_dict)
