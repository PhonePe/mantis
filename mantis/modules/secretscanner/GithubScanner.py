import logging
import sys

from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.modules.secretscanner.submodules.git_operation import GitOperation
from mantis.utils.tool_utils import get_assets_grouped_by_type, get_secret_by_url
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN
from mantis.config_parsers.config_client import ConfigProvider

'''
Secret Scanner module takes input as TLDs, crawls js files using gau and finds secrets
in them using gitleaks.
Output: gitleaks report
Information inserted
'''


class GithubScanner(BaseScanner):
    # Burp Proxy
    http_proxy = "http://127.0.0.1:8083"
    https_proxy = "http://127.0.0.1:8083"
    proxyDict = {
        "http": http_proxy,
        "https": https_proxy,
    }

    async def init(self, args: ArgsModel):
        self.args = args
        self.domains = await get_assets_grouped_by_type(self, args, ASSET_TYPE_SUBDOMAIN)
        self.methods = ConfigProvider.get_config().secretscanner.github_method
        return [(self, "GithubScanner")]

    async def execute(self, tool_tuple):
        results = {}
        try:
            results["success"] = 0
            results["failure"] = 0
            scanner = GitOperation(self.args,self.methods)
            if "org" in self.methods:
                await scanner.org_scan()
            if "public" in self.methods:
                await scanner.public_scan(self.domains)
            results["success"] = 1
            results["failure"] = 0
            return results
        except Exception as e:
            results["exception"] = str(e)
            results["failure"] = 1
            results["success"] = 0
            return  results