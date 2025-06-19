from mantis.constants import ASSET_TYPE_SUBDOMAIN
from mantis.utils.crud_utils import CrudUtils
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD
import json
import os
import logging

'''
Tool Author: Abhinandan Khurana
Github: github.com/abhinandan-khurana
Tool Link: github.com/abhinandan-khurana/go-wayback

Go_Wayback module enumerates subdomain of the TLDs which are fetched from database. 
Output file: .txt 
Each subdomain discovered is inserted into the database as a new asset. 
'''

class Go_Wayback(ToolScanner):

    def __init__(self) -> None:
        super().__init__()
        
    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = 'go-wayback  -o {output_file_path} -subdomain {input_domain}'
        self.outfile_extension = ".txt"
        self.assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return super().base_get_commands(self.assets)
    
    def clean_url(self, url):
        """Clean URL to extract subdomain only."""
        # Remove protocol if present
        if '://' in url:
            url = url.split('://')[-1]
        
        # Remove URL parameters and paths
        url = url.split('?')[0]
        url = url.split('/')[0]
        
        # Remove port numbers if present
        url = url.split(':')[0]
        
        return url.strip()

    def parse_report(self, outfile):
        output_dict_list = []
        wayback_output = open(outfile).readlines()
        seen_domains = set()  # To avoid duplicates
        
        for domain in wayback_output:
            clean_domain = self.clean_url(domain.rstrip('\n'))
            
            # Skip if domain already processed or empty
            if not clean_domain or clean_domain in seen_domains:
                continue
                
            seen_domains.add(clean_domain)
            domain_dict = {
                '_id': clean_domain,
                'asset': clean_domain,
                'asset_type': ASSET_TYPE_SUBDOMAIN,
                'org': self.org,
                'tools_source': 'go-wayback'
            }
            output_dict_list.append(domain_dict)
        return output_dict_list
    
    async def db_operations(self, tool_output_dict, asset=None):
        await CrudUtils.insert_assets(tool_output_dict)