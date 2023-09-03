import json
import logging
from mantis.utils.crud_utils import CrudUtils
from mantis.models.args_model import ArgsModel
from mantis.utils.common_utils import CommonUtils
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.utils.tool_utils import get_assets_with_non_empty_fields
from mantis.config_parsers.config_client import ConfigProvider

'''
NucleiInfo module is used to run the informational scan 
'''

class NucleiInfo(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    async def get_commands(self,args: ArgsModel):
        self.org = args.org
        whitelist = ConfigProvider.get_config().nuclei_template_path.whitelist
        blacklist = ConfigProvider.get_config().nuclei_template_path.blacklist
        self.base_command = 'nuclei -u {input_domain} -jle {output_file_path} -v -et http/technologies/ -exclude-severity low, medium, high, critical, unknown -hm'
        
        if whitelist is not None:
            whitelist_command = ' -t {}'.format(whitelist)
            self.base_command += whitelist_command
        if blacklist is not None:
            blacklist_command = ' -et {}'.format(blacklist)
            self.base_command += blacklist_command

        self.outfile_extension = ".json"
        self.assets = await get_assets_with_non_empty_fields(args, "active_hosts")
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
        report_dict = []
        nuclei_info = []

        # Convert json lines file to dict
        with open(outfile) as json_lines:
            for line in json_lines:
                report_dict.append(json.loads(line))
        if report_dict:
            for every_vuln in report_dict:
                nuclei = {}
                logging.info(f'Every vulnerability - {every_vuln}')
                nuclei["type"] = "informational"
                nuclei["org"] = self.org
                nuclei['title'] = every_vuln['template-id']

                if 'description' in every_vuln:
                    nuclei['description'] = every_vuln['info']['description']
                else:
                    nuclei['description'] = "null"
                
                nuclei['info'] = every_vuln['info']

                if 'severity' in every_vuln['info']:
                    nuclei['severity'] = every_vuln['info']['severity']
                else:
                    nuclei['severity'] = "null"
                
                if 'cve_id' in every_vuln:
                    nuclei['cve_id'] = every_vuln['info']['classification']['cve-id']
                else:
                    nuclei['cve_id'] = "null"

                if 'cwe_id' in every_vuln:
                    nuclei['cwe_id'] = every_vuln['info']['classification']['cwe-id']
                else:
                    nuclei['cwe_id'] = "null"

                nuclei['host_with_protocol'] = every_vuln['host']

                nuclei['remediation'] = "null"
                
                nuclei_info.append(nuclei)

            return nuclei_info
        else:
            logging.debug('Nuclei output file found, but no vulnerabilities were reported')
    
    async def db_operations(self, output_dict, asset=None):

        await CrudUtils.insert_findings(self, asset, output_dict)
