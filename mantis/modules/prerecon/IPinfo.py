import json
import logging
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.utils.crud_utils import CrudUtils
from mantis.models.args_model import ArgsModel
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN, ASSET_TYPE_IP

'''
IPinfo Module fetches the ip information for the TLDS, subdomain and IP
Output: JSON file
Information inserted into DB:
- hostname
- location with latitude and longitude
- country name
'''

class IPinfo(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    async def get_commands(self, args: ArgsModel):
        self.token = None
        if self.token is None:
            logging.warning("IPinfo token not provided, IPinfo will not run successfully")
            raise Exception("IPinfo token not provided!!")
        self.org = args.org
        self.std = "PIPE"
        self.base_command = 'dig +short {input_domain} | ipinfo bulk  --token ' + self.token + '| tee {output_file_path}'
        self.outfile_extension = ".json"
        self.assets = await get_assets_grouped_by_type(args, ASSET_TYPE_TLD)
        self.assets.extend(await get_assets_grouped_by_type(args, ASSET_TYPE_SUBDOMAIN))
        self.assets.extend(await get_assets_grouped_by_type(args, ASSET_TYPE_IP))

        return super().base_get_commands(self.assets)
    
    
    def parse_report(self, outfile):

        tool_output_dict = {}
        tool_output_dict["ipinfo"] = {}
        with open(outfile) as json_file:
            report_dict = json.load(json_file)

        for ip in report_dict:
            ip_dict = {}
            ip_dict[ip] = {}
            if 'hostname' in report_dict[ip]:
                ip_dict[ip]['hostname'] = report_dict[ip]['hostname']
            if 'country_name' in report_dict[ip]:    
                ip_dict[ip]['country_name'] = report_dict[ip]['country_name']
            if 'loc' in report_dict[ip]:
                lat, long = report_dict[ip]["loc"].split(',')
                ip_dict[ip]["ip_location"] = {"lat": float(lat), "long": float(long)}

            tool_output_dict["ipinfo"].update(ip_dict)
            
        return tool_output_dict

    async def db_operations(self, tool_output_dict, asset=None):
        await CrudUtils.update_asset(asset=asset, org=self.org, tool_output_dict=tool_output_dict)
        