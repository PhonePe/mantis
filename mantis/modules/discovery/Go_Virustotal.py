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
Tool Link: github.com/abhinandan-khurana/go_virustotal

Go_Virustotal module enumerates subdomain of the TLDs which are fetched from database. 
Output file: .json 
------------------
   1   │ {
   2   │   "tool_name": "virustotal",
   3   │   "result": [
   4   │     {
   5   │       "domain_name": "example.com",
   6   │       "results": [
   7   │         "blog.example.com",
   8   │         "internal.example.example",
   9   │         "dc-admin.example.com",
  10   │         "www.example.com"
  11   │       ]
  12   │     }
  13   │   ]
  14   │ }
------------------
Each subdomain discovered is inserted into the database as a new asset. 
'''

class Go_Virustotal(ToolScanner):

    def __init__(self) -> None:
        super().__init__()
        
    async def get_commands(self, args: ArgsModel):
        self.VT_API_KEY = None # Provide the VT_API_KEY (Virustotal API key) token here
        if self.VT_API_KEY is None:
            logging.warning("VT_API_KEY token not exported, Go_Virustotal will not run successfully")
            raise Exception("VT_API_KEY token not provided!!")
        else:
            os.environ['VT_API_KEY'] = self.VT_API_KEY
        self.org = args.org
        self.base_command = 'go_virustotal -domain {input_domain} -silent -json > {output_file_path}'
        self.outfile_extension = ".json"
        self.assets = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        
        return super().base_get_commands(self.assets)
    
    def parse_report(self, outfile):
        output_dict_list = []
        
        # Read and parse JSON file
        with open(outfile) as f:
            vt_output = json.load(f)
            print("VTTTT",vt_output)
        
        # Process each domain result
        for domain_obj in vt_output['result']:
            for subdomain in domain_obj['results']:
                domain_dict = {
                    '_id': subdomain,
                    'asset': subdomain,
                    'asset_type': ASSET_TYPE_SUBDOMAIN,
                    'org': self.org,
                    'tool_source': 'Go_Virustotal'
                }
                output_dict_list.append(domain_dict)
        return output_dict_list
    
    async def db_operations(self, tool_output_dict, asset=None):
        await CrudUtils.insert_assets(tool_output_dict)