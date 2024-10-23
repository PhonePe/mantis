import logging
import requests
import json
from lxml import etree
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN
from mantis.models.args_model import ArgsModel
from mantis.utils.asset_type import AssetType
from mantis.utils.crud_utils import CrudUtils
from mantis.utils.base_request import BaseRequestExecutor
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.utils.list_assets import ListAssets
from mantis.tool_base_classes.baseScanner import BaseScanner


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

namecheap_api_url = 'https://api.namecheap.com/xml.response'

api_user = None
user_name = None
api_key = None
client_ip = None

class Namecheap(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        self.db_assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return [(self, "Namecheap")]

    async def execute(self, tooltuple):
        logging.info(f"Reading zone files from Namecheap nameservers")
        return await self.main()

    def namecheap_dns_request(self, sld, tld):
        data = {
            'ApiUser': api_user,
            'UserName': user_name,
            'ApiKey': api_key,
            'ClientIP': client_ip,
            'Command': 'namecheap.domains.dns.getHosts',
            'SLD': sld,
            'TLD': tld
        }
        
        url = f"{namecheap_api_url}?{requests.compat.urlencode(data)}"
        api_tuple = (url, None, None, {"sld": sld, "tld": tld})
        _, response = BaseRequestExecutor.sendRequest("GET", api_tuple)
        response_xml = etree.XML(response.content)

        if response_xml.get('Status') != 'OK':
            logging.info("Error in response from Namecheap")
            raise Exception(response.content)

        return response_xml

    def namecheap_domain_request(self):
        data = {
            'ApiUser': api_user,
            'UserName': user_name,
            'ApiKey': api_key,
            'ClientIP': client_ip,
            'Command': 'namecheap.domains.getList',
            'Page': 1,
            'PageSize': 100
        }
        
        url = f"{namecheap_api_url}?{requests.compat.urlencode(data)}"
        api_tuple = (url, None, None, None)
        _, response = BaseRequestExecutor.sendRequest("GET", api_tuple)
        response_xml = etree.XML(response.content)

        if response_xml.get('Status') != 'OK':
            logging.info("Error in response from Namecheap")
            raise Exception(response.content)

        return response_xml

    def get_records(self, sld, tld):
        response = self.namecheap_dns_request(sld, tld)
        host_elements = response.xpath(
            '/x:ApiResponse/x:CommandResponse/x:DomainDNSGetHostsResult/x:host',
            namespaces={'x': 'http://api.namecheap.com/xml.response'}
        )
        
        records = [dict(h.attrib) for h in host_elements]
        for record in records:
            record.pop('AssociatedAppTitle', None)
            record.pop('FriendlyName', None)
            record.pop('HostId', None)
            record['HostName'] = record.pop('Name') + '.' + sld + '.' + tld
            record.pop('IsActive', None)
            record.pop('IsDDNSEnabled', None)
            if record['Type'] != 'MX':
                record.pop('MXPref', None)
            record['RecordType'] = record.pop('Type')
            if record['TTL'] == '1800':
                record.pop('TTL')
        return records

    async def main(self):
        results = {}
        output_dict_list = []
        results["success"] = 0
        results["failure"] = 0

        # Fetch domains from Namecheap
        request = self.namecheap_domain_request()
        domains = request.xpath(
            '//x:DomainGetListResult/x:Domain/@Name', 
            namespaces={'x': 'http://api.namecheap.com/xml.response'}
        )

        logging.info(f"Current Domains in scope added to org: {self.db_assets}")
        logging.info(f"Domains registered in Namecheap: {domains}")

        for domain in domains:
            (sld, tld) = domain.split('.', 1)

            # If using the --in_scope/-is arguments, list only domains from nameserver that are in scope
            if self.args.in_scope == True and domain not in self.db_assets:
                logging.info(f"Asset {domain} not in scope. Skipping...")
                continue

            logging.info(f'Enumerating domain: {domain}')

            try:
                records = self.get_records(sld, tld)
                for record in records:
                    domain_dict = {}
                    domain_dict['_id'] = record['HostName']
                    domain_dict['asset'] = record['HostName']

                    if AssetType.check_tld(record['HostName']):
                        domain_dict['asset_type'] = ASSET_TYPE_TLD
                    else:
                        domain_dict['asset_type'] = ASSET_TYPE_SUBDOMAIN
                    
                    domain_dict['org'] = self.args.org
                    output_dict_list.append(domain_dict)
                    results["success"] += 1 
            
            except Exception as e:
                logging.info(f"Enumeration for {domain} failed: {e}")
                results["failure"] += 1
                results['exception'] = str(e)

                err = e.args[0].decode("utf-8").encode()
                logging.info(err)
                API_exception = etree.fromstring(err)
                error_code = API_exception.find('.//{http://api.namecheap.com/xml.response}Error').get('Number')

                logging.info(error_code)
                # Continue with scanning other domains if DNS is misconfigured.
                # Terminate if any other error in API response.
                # Error Code: 2030288 - Cannot complete this command as this domain is not using proper DNS servers
                # Read more: https://www.namecheap.com/support/api/methods/domains-dns/get-hosts/
                if error_code != 2030288:
                    raise Exception(f"Error in response from Namecheap API: {e}")
                    return results
        
        await CrudUtils.insert_assets(output_dict_list, source='internal')
        logging.info("Inserted into the database.")
        return results
