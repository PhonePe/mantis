import logging
import requests
import json
from lxml import etree
from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.asset_type import AssetType
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN
from mantis.utils.crud_utils import CrudUtils
from mantis.utils.base_request import BaseRequestExecutor
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.utils.list_assets import ListAssets


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

namecheap_api_url = 'https://api.namecheap.com/xml.response'

api_user = None
user_name = None
api_key = None
client_ip = None


class Namecheap(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
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
            raise Exception(f"Error in response from Namecheap: {response.content}")

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
            raise Exception(f"Error in response from Namecheap: {response.content}")

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

        for domain in domains:
            (sld, tld) = domain.split('.', 1)
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
            
            except Exception as e:
                logging.info("Failed")
                results["failure"] = 1
                results['exception'] = str(e)
                return results
        
        await CrudUtils.insert_assets(output_dict_list, source='internal')
        logging.info("Inserted into the database.")
        results["success"] = 1    
        return results
