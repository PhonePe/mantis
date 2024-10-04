import os
import logging
import argparse
from itertools import count
import json
from lxml import etree
import requests
import sys
import yaml
from mantis.config_parsers.config_client import ConfigProvider
from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.asset_type import AssetType
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN
from mantis.utils.crud_utils import CrudUtils

'''
namecheap-export-dns-records.py - Extract DNS records from Namecheap

This script can export DNS records from a domain in Namecheap and print the domains detected.
python namecheap-export-dns-records.py

To use the script you need to enable the Namecheap API on your account and
whitelist the public IPv4 address of the host you're running the script on. See
https://www.namecheap.com/support/api/intro/ for details.

You need to provide valid Namecheap API details in the global variables.
'''

class Namecheap(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        return [(self, "Namecheap")]
    
    async def execute(self, tooltuple):
        #logging.info(f"Using credentials from {os.environ['AWS_SHARED_CREDENTIALS_FILE']}")
        logging.info(f"Reading zone files from Namecheap nameservers")
        return await self.main()

    async def main(self):
        """This script dumps all the domain names (hostnames) for all hosted zones on a Namecheap instance \n

        Prerequisite for this script - Namecheap API details need to be present in global variables \n
        
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        namecheap_api_url = 'https://api.namecheap.com/xml.response'

        #api_user = "<namecheap_api_username>"
        #user_name = "<namecheap_account_username>"
        #api_key = "<namecheap_api_key>"
        #client_ip = "<whitelisted_client_ip_address>" # Client IP white-listing is mandatory in Namecheap

        output_dict_list = []
        results = {}
        results["success"] = 0
        results["failure"] = 0

        try:

            domain = "example.org"
            (sld, tld) = domain.split('.', 1)
            logging.info(f'Enumerating domain: {domain}')
            records = do_export(sld,tld)

            for subdomain in records:
                domain_dict = {}
                domain_dict['_id'] = subdomain
                domain_dict['asset'] = subdomain
                if AssetType.check_tld(subdomain):
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

    def make_namecheap_request(data):
        request = data.copy()
        request.update({
            'ApiUser': api_user,
            'UserName': user_name,
            'ApiKey': api_key,
            'ClientIP': client_ip,
        })
        response = requests.post(namecheap_api_url, request)
        response.raise_for_status()
        response_xml = etree.XML(response.content)
        if response_xml.get('Status') != 'OK':
            raise Exception('Bad response: {}'.format(response.content))
        return response_xml

    def get_records(sld, tld):
        response = make_namecheap_request({
            'Command': 'namecheap.domains.dns.getHosts',
            'SLD': sld,
            'TLD': tld})
        host_elements = response.xpath(
            '/x:ApiResponse/x:CommandResponse/x:DomainDNSGetHostsResult/x:host',
            namespaces={'x': 'http://api.namecheap.com/xml.response'})
        records = [dict(h.attrib) for h in host_elements]
        for record in records:
            record.pop('AssociatedAppTitle', None)
            record.pop('FriendlyName', None)
            record.pop('HostId', None)
            record['HostName'] = record.pop('Name')+"."+sld+"."+tld
            record.pop('IsActive', None)
            record.pop('IsDDNSEnabled', None)
            if record['Type'] != 'MX':
                record.pop('MXPref', None)
            record['RecordType'] = record.pop('Type')
            if record['TTL'] == '1800':
                record.pop('TTL')
        return records

    def do_export(sld,tld):
        records = get_records(sld,tld)
        return records
        # for record in records:
        #     print(record['HostName'])

    def dict_hash(d):
        d = d.copy()
        name = d.pop('HostName')
        type_ = d.pop('RecordType')
        return (type_, name, json.dumps(d, sort_keys=True))
            