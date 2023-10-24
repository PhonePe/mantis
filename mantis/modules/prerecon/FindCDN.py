import json
from mantis.utils.crud_utils import CrudUtils
from mantis.models.args_model import ArgsModel
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN

'''
FindCDN Module discovers the CDN used by the TLDs and subdomains. 
TLDs and subdomains are fetched from the DB
Output: JSON file
Information inserted in DB:
- cdn_names
'''

class FindCDN(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = 'findcdn list {input_domain} -o {output_file_path} -v'
        self.outfile_extension = ".json"
        self.assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        self.assets.extend(await get_assets_grouped_by_type(self, args, ASSET_TYPE_SUBDOMAIN))
        return super().base_get_commands(self.assets)
    
    
    def parse_report(self, outfile):

        tool_output_dict = {}
        
        with open(outfile) as json_file:
            report_dict = json.load(json_file)

        cdn_info = report_dict['domains']
        tool_output_dict['cdn_names'] = []
        for domain_name, values in cdn_info.items():
            cdns = values['cdns_by_names']
            cdns = cdns.replace('\'', '').replace(' ','')
            tool_output_dict['cdn_names'].extend(set(cdns.split(',')))
            
        return tool_output_dict

    async def db_operations(self, tool_output_dict, asset=None):
        await CrudUtils.update_asset(asset=asset, org=self.org, tool_output_dict=tool_output_dict)
        