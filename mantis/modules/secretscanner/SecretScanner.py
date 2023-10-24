import logging
from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.modules.secretscanner.submodules.gau import Gau
from mantis.modules.secretscanner.submodules.url_downloader import URLDownloader
from mantis.modules.secretscanner.submodules.json_converter import JSONConverter
from mantis.modules.secretscanner.submodules.gitleaks_runner import GitleaksRunner
from mantis.modules.secretscanner.submodules.secret_finder import SecretFinder
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD

'''
Secret Scanner module takes input as TLDs, crawls js files using gau and finds secrets 
in them using gitleaks. 
Output: gitleaks report
Information inserted
'''

class SecretScanner(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        self.domains = await get_assets_grouped_by_type(self, args, ASSET_TYPE_TLD)
        return [(self, "SecretScanner")]
        
    async def execute(self, tool_tuple):
        results = {}
        try: 
            path = await Gau.process_domains(args=self.args)
            await URLDownloader.process_urls(args=self.args, path=path)
            await JSONConverter.convert_to_json_array(args=self.args, path=path)
            await GitleaksRunner.process_domains(args=self.args, path=path)
            results["success"] = 0
            results["failure"] = 0
            for domain in self.domains:
                try:
                    secret_finder = SecretFinder(domain, self.args, path)
                    await secret_finder.find_secrets_and_urls()
                    results["success"] += 1
                except Exception as e:
                    results["exception"] = str(e)
            logging.info(f"Deleting the secrets folder {path}")

            return results
        except Exception as e:
            results["exception"] = str(e)
            return results
