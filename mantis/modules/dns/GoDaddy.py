import logging
import requests
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN
from mantis.models.args_model import ArgsModel
from mantis.utils.asset_type import AssetType
from mantis.utils.crud_utils import CrudUtils
from mantis.utils.base_request import BaseRequestExecutor
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.tool_base_classes.baseScanner import BaseScanner


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

godaddy_api_url = 'https://api.godaddy.com/v1'

# Edit these values with your GoDaddy API credentials.
# Create an API key at https://developer.godaddy.com/keys (API type: Production, Scope: domains)
godaddy_api_key = None
godaddy_api_secret = None

'''
GoDaddy module is used to fetch the subdomains from the GoDaddy nameserver.
Output: List of subdomains
The discovered subdomains are inserted into db.
Source is marked as internal in this case. 
'''


class GoDaddy(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        self.db_assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return [(self, "GoDaddy")]

    async def execute(self, tooltuple):
        logging.info(f"Reading zone files from GoDaddy nameservers")
        return await self.main()

    # To get the list of all domains registered in the GoDaddy account (paginated)
    def get_domains(self, headers):
        domains = []
        marker = ""
        while True:
            query = {"limit": "1000"}
            if marker:
                query["marker"] = marker
            url = f"{godaddy_api_url}/domains?{requests.compat.urlencode(query)}"
            api_tuple = (url, headers, None, None)
            _, response = BaseRequestExecutor.sendRequest("GET", api_tuple)

            if response.status_code not in range(200, 299):
                raise Exception(f"Error in response from GoDaddy API: {response.content}")

            batch = response.json()
            if not batch:
                break

            domains.extend(domain['domain'] for domain in batch)

            if len(batch) < 1000:
                break
            marker = batch[-1]['domain']

        return domains

    # To get the list of all DNS records for a domain registered in the GoDaddy account
    def get_records(self, domain, headers):
        url = f"{godaddy_api_url}/domains/{domain}/records"
        api_tuple = (url, headers, None, None)
        _, response = BaseRequestExecutor.sendRequest("GET", api_tuple)

        if response.status_code not in range(200, 299):
            raise Exception(f"Error in response from GoDaddy API for {domain}: {response.content}")

        return response.json()

    async def main(self):
        results = {}
        output_dict_list = []
        results["success"] = 0
        results["failure"] = 0

        try:
            if godaddy_api_key is None or godaddy_api_secret is None:
                results["failure"] = 1
                results['exception'] = "GoDaddy API credentials not set in mantis/modules/dns/GoDaddy.py"
                logging.error("[!] " + results['exception'])
                return results

            headers = {"Authorization": f"sso-key {godaddy_api_key}:{godaddy_api_secret}"}

            # Fetch domains from GoDaddy
            domains = self.get_domains(headers)

            logging.info(f"Current Domains in scope added to org: {self.db_assets}")
            logging.info(f"Domains registered in GoDaddy: {domains}")

            hostnames = set()  # Empty set for appending hostnames later
            for domain in domains:

                # If using the --in_scope/-is arguments, list only domains from nameserver that are in scope
                if self.args.in_scope == True and domain not in self.db_assets:
                    logging.info(f"Asset {domain} not in scope. Skipping...")
                    continue

                logging.info(f'Enumerating domain: {domain}')

                try:
                    records = self.get_records(domain, headers)
                    for record in records:
                        name = record.get('name')
                        # Filter out non-hostname records i.e. with '_', '\' etc and wildcards
                        if name is None or any(c in name for c in ['_', '\\', '*']):
                            continue
                        if name == '@' or name == '':
                            hostname = domain
                        else:
                            hostname = f"{name}.{domain}"
                        hostnames.add(hostname)
                    results["success"] += 1

                except Exception as e:
                    logging.info(f"Enumeration for {domain} failed: {e}")
                    results["failure"] += 1
                    results['exception'] = str(e)

            for hostname in hostnames:
                domain_dict = {}
                domain_dict['_id'] = hostname
                domain_dict['asset'] = hostname

                if AssetType.check_tld(hostname):
                    domain_dict['asset_type'] = ASSET_TYPE_TLD
                else:
                    domain_dict['asset_type'] = ASSET_TYPE_SUBDOMAIN

                domain_dict['org'] = self.args.org
                output_dict_list.append(domain_dict)

            await CrudUtils.insert_assets(output_dict_list, source='internal')
            logging.info("Inserted into the database.")

        except Exception as e:
            results["failure"] = 1
            results['exception'] = str(e)
            logging.error("[!] Error in GoDaddy module - {}".format(str(e)))

        return results
