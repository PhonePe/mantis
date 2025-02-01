from mantis.constants import ASSET_TYPE_SUBDOMAIN
from mantis.utils.crud_utils import CrudUtils
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD

'''
Subfinder module enumerates subdomain of the TLDs which are fetched from database. 
Output file: .txt separated by new line. 
Each subdomain discovered is inserted into the database as a new asset. 
'''

class Subfinder(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = 'subfinder -d {input_domain} -o {output_file_path}'
        self.outfile_extension = ".txt"
        self.assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return super().base_get_commands(self.assets)
    
    def parse_report(self,outfile):
        output_dict_list = []
        subfinder_output = open(outfile).readlines()
        for domain in subfinder_output:
            domain_dict = {}
            domain_dict['_id'] = domain.rstrip('\n')
            domain_dict['asset'] = domain.rstrip('\n')
            domain_dict['asset_type'] = ASSET_TYPE_SUBDOMAIN
            domain_dict['org'] = self.org
            domain_dict['tools_source'] = 'subfinder'
            output_dict_list.append(domain_dict)
        return output_dict_list
    
    async def db_operations(self, tool_output_dict, asset=None):
        await CrudUtils.insert_assets(tool_output_dict)
