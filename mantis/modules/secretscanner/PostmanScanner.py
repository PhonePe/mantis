import logging
import json
from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD
from porchpirate import porchpirate
from mantis.utils.crud_utils import CrudUtils

'''
Postman Scanner module takes input as TLDs  
Output: Postman report
Information inserted
'''

class PostmanScanner(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        self.domains = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return [(self, "PostmanScanner")]

    async def execute(self, tool_tuple):
        results = {}
        self.finding_type = 'api_collection'
        findings=[]
        p = porchpirate()
        try:
            for tld in self.domains:
                print("x: ", tld)
                search_results = json.loads(p.search(tld))
                for search_result in search_results['data']:
                    # print("Search result:: ", search_result)
                    finding = {}
                    finding['host'] = tld
                    finding['title'] = 'Public Postman Collection Discovered'
                    finding['org'] = self.args.org
                    finding['type'] = self.finding_type
                    finding['tool_source'] = 'PostmanScanner'
                    finding["info"] = ""
                    if self.args.app:
                        finding['app'] = self.args.app
                    if search_result['document']['publisherHandle'] and len(search_result['document']['publisherHandle']):
                        finding['url'] = 'https://www.postman.com/' + search_result['document']['publisherHandle'] 
                    finding['others']={}
                    if search_result['document']['url']:
                        finding['others']['postman_url'] = search_result['document']['url']
                    if search_result['document']['publisherName']: 
                        finding['others']['publisherName'] = search_result['document']['publisherName'] 
                    # if search_result['document']['warehouse__updated_at_request']:
                    #     finding['others']['warehouse__updated_at_request'] = search_result['document']['warehouse__updated_at_request']
                    if search_result['document']['workspaces']:
                        finding['others']['workspaces'] = search_result['document']['workspaces']
                    if search_result['document']['collection']:  
                        finding['others']['collection'] = search_result['document']['collection'] 
                    if search_result['document']['name']:
                        finding['others']['name'] = search_result['document']['name'] 

                    findings.append(finding)
            print("Findings::: ", len(findings))
            if len(findings):
                results["success"] = 1
                results["failure"] = 0
                logging.debug("Inserting postman data in db.")
                await CrudUtils.insert_findings(self, None, findings, self.finding_type)
            else:
                logging.debug('No public postman collections found')
            logging.debug("Findings inserted in db") 
            return results
        except Exception as e:
            results["failure"] = 1
            results["success"] = 0
            results["exception"] = str(e)
            logging.error(f"Error occurred while parsing porch pirate result: {e}")

            return results



    