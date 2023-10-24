from mantis.tool_base_classes.apiScanner import APIScanner
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN
from mantis.models.args_model import ArgsModel
from mantis.utils.crud_utils import CrudUtils

'''
Csper Module is used to get the CSP misconfigurations for the TLD and subdomains. 
Output: Response to the csper.io API. 
Information inserted in DB:
- csp directives
'''

class Csper(APIScanner):

    async def get_api_calls(self, args: ArgsModel):
        self.asset_api_list = []
        self.scannerName = type(self).__name__
        self.endpoint = 'https://csper.io/api/evaluations'
        self.body = {"URL":"https://{asset}"}
        self.org = args.org
        self.assets.extend(await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD))
        self.assets.extend(await get_assets_grouped_by_type(self, args, ASSET_TYPE_SUBDOMAIN))
        for every_asset in self.assets:
            body_param = self.body["URL"].format(asset=every_asset)
            # Append tuple with endpoint, headers, body, asset
            self.asset_api_list.append((self.endpoint, None, body_param, every_asset))

        return [(self, "GET")]
    

    def parse_reponse(self, response):
        findings = []
        response_json = response.json()
        recommendations = response_json[0]['recommendations']
        for recommendation in recommendations:
            finding_dict = {}
            finding_dict["title"] = recommendation["title"]
            finding_dict["type"] = "misconfiguration"
            finding_dict["severity"] = recommendation["severity"]
            finding_dict["remediation"] = recommendation["recommendation"]
            finding_dict["others"] = {}
            finding_dict["others"]["directive"] = recommendation["directive"]
            finding_dict["org"] = self.org
            ## to set tool source
            findings.append(finding_dict)
        return findings


    async def db_operations(self, output_dict, asset=None):
        await CrudUtils.insert_findings(self, asset, output_dict)
