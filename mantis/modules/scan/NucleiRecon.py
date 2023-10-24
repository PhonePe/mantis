import logging
import json
from mantis.utils.crud_utils import CrudUtils
from mantis.models.args_model import ArgsModel
from mantis.utils.common_utils import CommonUtils
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.utils.tool_utils import get_assets_with_non_empty_fields

'''
THIS MODULE IS NOT IN USE AS OF NOW
NucleiRecon Module is used to run only technologies templates of nuclei on the target
Output: JSON file
Information inserted into DB:
- technologies
'''

class NucleiRecon(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    async def get_commands(self,args: ArgsModel):
        self.org = args.org
        self.base_command = 'nuclei -u {input_domain} -jle {output_file_path} -t http/technologies/  -hm -v'
        self.outfile_extension = ".json"
        self.assets = await get_assets_with_non_empty_fields(self, args, "active_hosts")
        self.commands_list = []
        for every_asset in self.assets:
            if "_id" in every_asset:
                domain = every_asset["_id"]
                for active_hosts in every_asset["active_hosts"][0]:
                    outfile = CommonUtils.generate_unique_output_file_name(domain, self.outfile_extension)
                    command = self.base_command.format(input_domain = active_hosts, output_file_path = outfile)
                    self.commands_list.append((self, command, outfile, domain))
            else:
                outfile = CommonUtils.generate_unique_output_file_name(every_asset, self.outfile_extension)
                command = self.base_command.format(input_domain = every_asset, output_file_path = outfile)
                self.commands_list.append((self, command, outfile, every_asset))
                
        return self.commands_list
    

    def parse_report(self, outfile):
        logging.debug(f'Parsing Nuclei Technology Recon for single domain - begins')

        report_list = []
        report_output_dict = {}
        
        with open(outfile) as json_lines:
            for line in json_lines:
                report_list.append(json.loads(line))
        
        if report_list:
            technologies = []
            for every_report in report_list:
                if 'matcher-name' in every_report:
                    technologies.append(every_report['matcher-name'])
            
            report_output_dict["technologies"] = list(set(technologies))      
               
        return report_output_dict    

    async def db_operations(self, tool_output_dict, asset):
        await CrudUtils.update_asset(asset=asset, org=self.org, tool_output_dict=tool_output_dict)
