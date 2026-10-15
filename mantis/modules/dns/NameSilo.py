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

namesilo_api_url = 'https://www.namesilo.com/api'

# Edit this value with your NameSilo API key.
# Generate one at https://www.namesilo.com/account/api-manager
namesilo_api_key = None

'''
NameSilo module is used to fetch the subdomains from the NameSilo nameserver.
Output: List of subdomains
The discovered subdomains are inserted into db.
Source is marked as internal in this case. 
'''


class NameSilo(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        self.db_assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return [(self, "NameSilo")]

    async def execute(self, tooltuple):
        logging.info(f"Reading zone files from NameSilo nameservers")
        return await self.main()

    # NameSilo returns a single item instead of a list when there is only one
    # entry; normalise both shapes into a list.
    @staticmethod
    def _as_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    # To get the list of all domains registered in the NameSilo account (paginated)
    def get_domains(self):
        domains = []
        page = 1
        while True:
            query = {
                "version": "1",
                "type": "json",
                "key": namesilo_api_key,
                "page": str(page),
                "pageSize": "100"
            }
            url = f"{namesilo_api_url}/listDomains?{requests.compat.urlencode(query)}"
            api_tuple = (url, None, None, None)
            _, response = BaseRequestExecutor.sendRequest("GET", api_tuple)

            if response.status_code not in range(200, 299):
                raise Exception(f"Error in response from NameSilo API: {response.content}")

            reply = response.json().get('reply', {})
            if reply.get('code') != 300:
                raise Exception(f"Error in response from NameSilo API: {reply.get('detail')}")

            batch = []
            for entry in self._as_list(reply.get('domains', {}).get('domain')):
                if isinstance(entry, dict):
                    entry = entry.get('domain') or entry.get('#text')
                if entry:
                    batch.append(str(entry))
            domains.extend(batch)

            if len(batch) < 100:
                break
            page += 1

        return domains

    # To get the list of all DNS records for a domain registered in the NameSilo account
    def get_records(self, domain):
        query = {"version": "1", "type": "json", "key": namesilo_api_key, "domain": domain}
        url = f"{namesilo_api_url}/dnsListRecords?{requests.compat.urlencode(query)}"
        api_tuple = (url, None, None, None)
        _, response = BaseRequestExecutor.sendRequest("GET", api_tuple)

        if response.status_code not in range(200, 299):
            raise Exception(f"Error in response from NameSilo API for {domain}: {response.content}")

        reply = response.json().get('reply', {})
        if reply.get('code') != 300:
            raise Exception(f"Error in response from NameSilo API for {domain}: {reply.get('detail')}")

        records = self._as_list(reply.get('records', {}).get('resource_record'))
        return [record for record in records if isinstance(record, dict)]

    async def main(self):
        results = {}
        output_dict_list = []
        results["success"] = 0
        results["failure"] = 0

        try:
            if namesilo_api_key is None:
                results["failure"] = 1
                results['exception'] = "NameSilo API key not set in mantis/modules/dns/NameSilo.py"
                logging.error("[!] " + results['exception'])
                return results

            # Fetch domains from NameSilo
            domains = self.get_domains()

            logging.info(f"Current Domains in scope added to org: {self.db_assets}")
            logging.info(f"Domains registered in NameSilo: {domains}")

            hostnames = set()  # Empty set for appending hostnames later
            for domain in domains:

                # If using the --in_scope/-is arguments, list only domains from nameserver that are in scope
                if self.args.in_scope == True and domain not in self.db_assets:
                    logging.info(f"Asset {domain} not in scope. Skipping...")
                    continue

                logging.info(f'Enumerating domain: {domain}')

                try:
                    records = self.get_records(domain)
                    for record in records:
                        host = record.get('host') or ''
                        # Filter out non-hostname records i.e. with '_', '\' etc and wildcards
                        if any(c in host for c in ['_', '\\', '*']):
                            continue
                        if host == '' or host == domain:
                            hostname = domain
                        elif host.endswith('.' + domain):
                            hostname = host
                        else:
                            hostname = f"{host}.{domain}"
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
            logging.error("[!] Error in NameSilo module - {}".format(str(e)))

        return results
