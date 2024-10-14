import os
import logging
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.config_parsers.config_client import ConfigProvider
from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.asset_type import AssetType
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN
from mantis.utils.crud_utils import CrudUtils
import CloudFlare 

'''
Cloudflare module is used to fetch the subdomains from the Cloudflare Nameserver.
Output: List of subdomains
The discovered subdomains are inserted into db.
Source is marked as internal in this case. 
'''

class Cloudflare(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        self.db_assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return [(self, "Cloudflare")]
    
    async def execute(self, tooltuple):
        #logging.info(f"Using credentials from {os.environ['AWS_SHARED_CREDENTIALS_FILE']}")
        logging.info(f"Reading zone files from Cloudflare nameservers")
        return await self.main()

    async def main(self):
        """This script dumps all the domain names (hostnames) for all hosted zones on a Cloudflare instance \n

        Prerequisite for this script - A CLoudflare DNS Zone Read only API key \n
        
        """
        token = None    #Edit the value with actual token
        per_page = 100
        output_dict_list = []
        results = {}
        results["success"] = 0
        results["failure"] = 0
        try:
            try:
                cf = CloudFlare.CloudFlare("", token, raw=True)
                zones = cf.zones.get(params={'per_page': per_page, 'page': 0})
                results["success"] += 1
            except Exception as e:
                results["failure"] += 1
                results["exception"] = str(e)
                logging.error("[!] Error - {}".format(str(e)))

            for zone_page in range(zones['result_info']['total_pages']):
                zones = cf.zones.get(params={'per_page': per_page, 'page': zone_page})
                for zone in zones['result']:
                    zone_id = zone['id']
                    zone_name = zone['name']
                    records = cf.zones.dns_records.get(zone['id'], params={'per_page': per_page, 'page': 1})
                for record_page in range(1, records['result_info']['total_pages']+1):
                    records = cf.zones.dns_records.get(zone['id'], params={'per_page': per_page, 'page': record_page})['result']
                    for record in records:
                        domain_dict = {}
                        if(self.args.in_scope == True):
                            print(self.db_assets)
                            for asset in self.db_assets:
                                if(asset in record['name']):
                                    domain_dict['_id'] = record['name']
                                    domain_dict['asset'] = record['name']
                                    if AssetType.check_tld(record['name']):
                                        domain_dict['asset_type'] = ASSET_TYPE_TLD
                                    else:
                                        domain_dict['asset_type'] = ASSET_TYPE_SUBDOMAIN
                                    domain_dict['org'] = self.args.org
                                    output_dict_list.append(domain_dict)
                                    break
                        else:
                            domain_dict['_id'] = record['name']
                            domain_dict['asset'] = record['name']
                            if AssetType.check_tld(record['name']):
                                domain_dict['asset_type'] = ASSET_TYPE_TLD
                            else:
                                domain_dict['asset_type'] = ASSET_TYPE_SUBDOMAIN
                            domain_dict['org'] = self.args.org
                            output_dict_list.append(domain_dict)
            await CrudUtils.insert_assets(output_dict_list, source='internal')
            results["success"] = 1
            return results
        
        except Exception as e:
            results["failure"] = 1
            results['exception'] = str(e)
            return results
            