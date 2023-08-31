from mantis.tool_base_classes.apiScanner import APIScanner
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_CERT
from mantis.models.args_model import ArgsModel
from mantis.utils.crud_utils import CrudUtils

'''
SSLMate module enumerates certifcates for the TLDs using certspotter API. 
Output: API response
Following information from the API response is added to the database:
- DNS Names
- tbs_sha256
- cert_sha256
- pubkey_sha256
- issuer
- not_before
- not_after
- revoked
- revocation
- cert_der
'''

class SSLMate(APIScanner):

    async def get_api_calls(self, args: ArgsModel):
        self.asset_api_list = []
        self.scannerName = type(self).__name__
        self.endpoint = "https://api.certspotter.com/v1/issuances?domain={domain_name}&include_subdomains=true&expand=dns_names&expand=issuer&expand=revocation&expand=problem_reporting&expand=cert_der"
        self.body = ""
        self.org = args.org
        self.assets.extend(await get_assets_grouped_by_type(args, ASSET_TYPE_TLD))
        for every_asset in self.assets:
            endpoint = self.endpoint.format(domain_name=every_asset)
            # send tuple in the form of endpoint, headers, body, asset
            self.asset_api_list.append((endpoint,None, None,  every_asset))
        return [(self, "GET")]
    

    def parse_reponse(self, response):
        output_dict_list = []
        response_json = response.json()
        for every_cert in response_json:
            cert_dict = {}
            cert_dict['asset'] = every_cert['id']
            cert_dict['asset_type'] = ASSET_TYPE_CERT
            cert_dict['org'] = self.org
            cert_dict['others'] = {}
            cert_dict['others']['dns_names'] = every_cert['dns_names']
            cert_dict['others']['tbs_sha256'] = every_cert['tbs_sha256']
            cert_dict['others']['cert_sha256'] = every_cert['cert_sha256']
            cert_dict['others']['pubkey_sha256'] = every_cert['pubkey_sha256']
            cert_dict['others']['issuer'] = every_cert['issuer']
            cert_dict['others']['not_before'] = every_cert['not_before']
            cert_dict['others']['not_after'] = every_cert['not_after']
            cert_dict['others']['revoked'] = every_cert['revoked']
            cert_dict['others']['revocation'] = every_cert['revocation']
            cert_dict['others']['cert_der'] = every_cert['cert_der']
            
            output_dict_list.append(cert_dict)

        return output_dict_list

    async def db_operations(self, output_dict, asset=None):
        await CrudUtils.insert_assets(output_dict)
