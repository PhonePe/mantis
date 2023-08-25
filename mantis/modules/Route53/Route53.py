import os
import boto3
import logging
import jmespath
from mantis.config_parsers.config_client import ConfigProvider
from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.asset_type import AssetType
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN
from mantis.utils.crud_utils import CrudUtils

'''
Route53 module is used to fetch the subdomains from the Route53 records.
Output: List of subdomains
The discovered subdomains are inserted into db.
Source is marked as internal in this case. 
'''
if ConfigProvider.get_config().aws.credentials_path is not None:
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = ConfigProvider.get_config().aws.credentials_path
else:
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '~/.aws/credentials'

if ConfigProvider.get_config().aws.config_path is not None:
    os.environ['AWS_CONFIG_FILE'] = ConfigProvider.get_config().aws.config_path
else:
    os.environ['AWS_CONFIG_FILE'] = '~/.aws/config'


class Route53(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        return [(self, "Route53")]
    
    async def execute(self, tooltuple):
        logging.info(f"Using credentials from {os.environ['AWS_SHARED_CREDENTIALS_FILE']}")
        logging.info(f"Using config from {os.environ['AWS_CONFIG_FILE']}")

        return await self.main()

    async def main(self):
        """This script dumps all the domain names (hostnames) for all hosted zones on a Route53 instance \n

        Prerequisite for this script - An AWS Named profile with ReadOnly permission to Route53 instance \n
        
        Usage - python3 route53-subdomain-dump.py aws_named_profile1 aws_named_profile2
        """
        results = {}
        results["success"] = 0
        results["failure"] = 0
        
        subdomains = [] # Empty list for appending subdomains later
        try:
            for profile in self.args.aws_profiles:
                try:
                    logging.info("[+] Enumerating subdomains for profiles - {}".format(profile))
                    session = boto3.Session(profile_name=profile)
                    results["success"] += 1
                except Exception as e:
                    results["failure"] += 1
                    results["exception"] = str(e)
                    logging.error("[!] Error in accessing AWS profile - {}".format(profile))
                    continue
                client = session.client('route53')
                hosted_zones = self.get_hosted_zone_ids(client, profile)
                resource_records = self.get_resource_records(hosted_zones, client, profile)
                subdomains = self.get_subdomains(resource_records, subdomains, profile)
            subdomains = set(subdomains) # remove duplicate subdomain
            output_dict_list = []
            for subdomain in subdomains:
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
        except Exception as e:
            results["failure"] = 1
            results['exception'] = str(e)

        return results

    # To get the list of all hosted zones on Route53 instance
    def get_hosted_zone_ids(self, client, profile):
        logging.info("[+] Getting all the hosted zones on Route53 instance for {}".format(profile))
        hosted_zones = []
        response = client.list_hosted_zones(
            MaxItems="300",
        )
        if ('HostedZones' in response.keys()
            and len(response['HostedZones'])) > 0:
            for i in response['HostedZones']:
                for key in i.keys():
                    if key=="Id":
                        hosted_zones.append(i[key].split('/')[2])
        else:
            logging.error("[+] Error in accessing hosted zones on Route53 instance for {}".format(profile))

        return hosted_zones

    # To get the list of all resouce record sets for the hosted zones on Route53 instance
    def get_resource_records(self, hosted_zones,client,profile):
        resource_record_sets = []
        #dns_record_types = ['SOA','A','TXT','NS','CNAME','MX','NAPTR','PTR','SRV','SPF','AAAA','CAA','DS']
        paginator = client.get_paginator('list_resource_record_sets')
        for hosted_zone in hosted_zones:
            logging.error("[+] Getting all the DNS resource records for {} - {}".format(hosted_zone, profile))
            paginated_resource_record_sets = paginator.paginate(HostedZoneId=hosted_zone)
            for record_set in paginated_resource_record_sets:
                resource_record_sets.append(record_set)
        
        return resource_record_sets

    # To extract subdomains (and filter out subdomains that are not hostnames i.e. with '_', '/' etc
    def get_subdomains(self, resource_records, subdomains, profile):
        logging.info("[+] Parsing the subdomains and extracting subdomains - {}".format(profile))
        for record in resource_records:
            parsed_records = jmespath.search("ResourceRecordSets[].Name",record)
            for parsed_record in parsed_records:
                if '_' not in parsed_record and '\\' not in parsed_record:
                    subdomains.append(parsed_record.rstrip('.'))
        return subdomains
