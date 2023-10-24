import json
import logging
import tldextract
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.crud_utils import CrudUtils
from mantis.constants import ASSET_TYPE_SUBDOMAIN, ASSET_TYPE_IP, ASSET_TYPE_TLD, ASSET_TYPE_THIRD_PARTY

class HTTPX(ToolScanner):

    def __init__(self) -> None:
        super().__init__()


    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = 'httpx -u {input_domain} -asn -json -o {output_file_path} -cname'
        self.outfile_extension = ".txt"
        self.assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_SUBDOMAIN)
        self.assets.extend(await get_assets_grouped_by_type(self, args, ASSET_TYPE_IP))
        self.db_assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return super().base_get_commands(self.assets)
    
    
    def parse_report(self, outfile):

        report_dict = {}
        tool_output_dict = {}

        with open(outfile) as json_lines:
            for line in json_lines:
                report_dict = json.loads(line)
        # for every_asset in report_dict:
        if 'asn' in report_dict:
            if 'as_number' in report_dict['asn']:
                tool_output_dict['as_number'] = report_dict['asn']['as_number']
            if 'as_name' in report_dict['asn']:
                tool_output_dict['as_name'] = report_dict['asn']['as_name']
            if 'as_country' in report_dict['asn']:
                tool_output_dict['as_country'] = report_dict['asn']['as_country']
            if 'as_range' in report_dict['asn']:
                tool_output_dict['as_range'] = report_dict['asn']['as_range']

        if 'tech' in report_dict:
            tool_output_dict['technologies'] = report_dict['technologies']
        
        if 'cname' in report_dict:
            tool_output_dict['dns'] = {}
            tool_output_dict['dns']['cname'] = report_dict['cname']

        if 'webserver' in report_dict:
            tool_output_dict['webserver'] = report_dict['webserver']

        if 'csp' in report_dict:
            self.third_party_integrations = []
            if 'domains' in report_dict['csp']:
                for csp_domain in report_dict['csp']['domains']:
                    csp_asset = tldextract.extract(csp_domain)
                    domain_tld = csp_asset.registered_domain
                    if csp_asset.subdomain:
                        third_party_domain = csp_asset.subdomain +'.'+ csp_asset.domain +'.'+ csp_asset.suffix
                    else:
                        third_party_domain = csp_asset.domain +'.'+ csp_asset.suffix
                    for tld in self.db_assets:
                        if domain_tld != tld and tld.split('.')[0] in third_party_domain:
                            third_party_integration = {}
                            third_party_integration['asset'] = third_party_domain
                            third_party_integration['asset_type'] = ASSET_TYPE_THIRD_PARTY
                            third_party_integration['org'] = self.org
                            self.third_party_integrations.append(third_party_integration)

        
        return tool_output_dict


    async def db_operations(self, tool_output_dict, asset):
        await CrudUtils.update_asset(asset=asset, org=self.org, tool_output_dict=tool_output_dict)
        if self.third_party_integrations:
            logging.debug("Inserting Third party integrations")
            await CrudUtils.insert_assets(self.third_party_integrations)
