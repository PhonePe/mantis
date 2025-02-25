import logging
import sys

from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.modules.secretscanner.submodules.git_operation import GitOperation
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN
from mantis.config_parsers.config_client import ConfigProvider

'''
Secret Scanner module takes input as TLDs, crawls js files using gau and finds secrets
in them using gitleaks.
Output: gitleaks report
Information inserted
'''


class GithubScanner(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        self.domains = await get_assets_grouped_by_type(self, args, ASSET_TYPE_SUBDOMAIN)
        self.methods = ConfigProvider.get_config().secretscanner.github_method
        return [(self, "GithubScanner")]

    async def execute(self, tool_tuple):
        results = {"success": 0, "failure": 0}
        try:

            # Run each method in self.methods
            for method in self.methods:
                scanner = GitOperation(self.args, method)

                if len(scanner.tokens) == 0:
                    logging.exception("Github tokens not present in local.yml")
                    raise Exception("Github token absent")
                if method == "org":
                    await scanner.org_scan()
                elif method == "public":
                    await scanner.public_scan(self.domains)

            results["success"] = 1  # Set success if all scans complete without errors
        except Exception as e:
            results["exception"] = str(e)
            results["failure"] = 1

        return results
