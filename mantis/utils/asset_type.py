import re
import tldextract
import logging
import sys
from ipaddress import ip_address, ip_network
from validators import domain
from netaddr import iter_iprange
from mantis.models.args_model import ArgsModel
from mantis.constants import ASSET_TYPE_SUBDOMAIN, ASSET_TYPE_IP, ASSET_TYPE_TLD

from mantis.utils.common_utils import CommonUtils

class AssetType:

    @staticmethod
    def assign_asset_type(assets: list, args: ArgsModel) -> list:
        
        assets_list = []

        for every_asset in assets:
            asset = {}
            every_asset = CommonUtils.strip_url_scheme(every_asset)
            asset['org'] = args.org 
            if AssetType.check_ip(every_asset):
                asset['asset'] = every_asset
                asset['type'] = ASSET_TYPE_IP
            elif AssetType.check_domain(every_asset):
                if AssetType.check_tld(every_asset):
                    asset['asset'] = every_asset
                    asset['type'] = ASSET_TYPE_TLD
                else:
                    asset['asset'] = every_asset
                    asset['type'] = ASSET_TYPE_SUBDOMAIN
            else:
                logging.warning(f"{every_asset} Invalid IP/Domain/CIDR/Range in input")
            
            assets_list.append(asset)

        logging.debug(f'Final List of Assets and Type - {assets_list}')
        return assets_list

    
    @staticmethod
    def check_ip(target):
        logging.debug(f"check_ip() - {target}")
        try:
            ip_address(target)
            logging.debug(f"{target} is an IPV4")
            return True
                
        except ValueError:
            logging.debug(f"valueError Exception: {target} is not an IPV4")
            return False


    @staticmethod
    def check_domain(target):
        logging.debug(f"check_domain() - {target}")
        if domain(target):
            logging.debug(f"{target} is a Domain")
            return True
        else:
            return False


    @staticmethod
    def check_tld(target):
        logging.debug(f"check_tld() - {target}")
        tld_extract = tldextract.extract(target).registered_domain
        if target == tld_extract:
            return True
        return False


    @staticmethod        
    def check_ip_cidr_regex(target):
        match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{1,2}", target)
        if match:
            return True
        else:
            logging.debug(f"ValueError Exception: {target} is not a valid IPV4 CIDR Regex")
            return False


    @staticmethod        
    def check_ip_cidr(target):
        try:
            ip_cidr = ip_network(target)
            logging.debug(f"{target} is an IPV4 CIDR")
            return True
        except ValueError:
            logging.debug(f"ValueError Exception: {target} is not a valid IPV4 CIDR")
            return False


    @staticmethod
    def check_ip_range(target):
        logging.debug(f"check_ip_range for target - {target}")
        match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\-[0-9]{1,2}", target)
        if match:
            return True
        else:
            return False


    @staticmethod        
    def expand_ip_cidr(target):
        logging.debug(f"expand_ip_cidr() - {target}")
        try:
            ip_subnet = ip_network(target)
            logging.debug(f"{target} is a valid IPV4 CIDR")
            ipv4_subnet_list = [str(ip).strip("IPv4Address('") for ip in ip_subnet.hosts()]
            logging.debug(f"Expanded IPV4 Subnet - {ipv4_subnet_list}")
            return ipv4_subnet_list
        except ValueError:
            logging.debug(f"valueError Exception: {target} is not an IPV4 subnet, Quitting!")
            sys.exit(1)


    @staticmethod
    def expand_ip_range(target):
        logging.debug(f"expand_ip_range() - {target}")
        try:
            first_ip = target.split('-')[0]
            last_ip_range = target.split('-')[1]
            last_ip = "%s.%s.%s.%s" % (
                first_ip.split('.')[0], first_ip.split('.')[1], first_ip.split('.')[2], last_ip_range)
            ip_range = list(iter_iprange(first_ip, last_ip))
            logging.debug(f"{target} is a IPV4 Range")
            ip_range = [str(ip).strip("IPAddress('") for ip in ip_range]
            logging.debug(f"Expanded IPV4 Range - {ip_range}")
            return ip_range
        except:
            logging.error(f"valueError Exception: {target} is not an IPV4 Range, Quitting !")
            exit(0)
