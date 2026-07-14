from mantis.constants import ASSET_TYPE_SUBDOMAIN
from mantis.utils.crud_utils import CrudUtils
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD

'''
puredns is a fast domain resolver and subdomain bruteforcing tool that can accurately filter out wildcard subdomains and DNS poisoned entries.
Output file: .txt separated by new line. 
Each subdomain discovered is inserted into the database as a new asset. 
'''


class Puredns(ToolScanner):

    def __init__(self) -> None:
        super().__init__()
        super().download_required_file()


    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = 'puredns bruteforce configs/resources/best-dns-wordlist.txt {input_domain} -r configs/resources/resolvers.txt --write {output_file_path}'
        self.outfile_extension = ".txt"
        self.assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return super().base_get_commands(self.assets)

    def parse_report(self, outfile):
        output_dict_list = []
        puredns_output = open(outfile).readlines()
        for domain in puredns_output:
            domain_dict = {}
            domain_dict['_id'] = domain.rstrip('\n')
            domain_dict['asset'] = domain.rstrip('\n')
            domain_dict['asset_type'] = ASSET_TYPE_SUBDOMAIN
            domain_dict['org'] = self.org
            domain_dict['tool_source'] = "Puredns"
            output_dict_list.append(domain_dict)

        return output_dict_list

    async def db_operations(self, tool_output_dict, asset=None):
        await CrudUtils.insert_assets(tool_output_dict)