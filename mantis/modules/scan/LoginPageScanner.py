import json
import logging
from mantis.tool_base_classes.apiScanner import APIScanner
from mantis.utils.tool_utils import get_assets_grouped_by_type, get_assets_with_non_empty_fields
from mantis.constants import ASSET_TYPE_SUBDOMAIN, ASSET_TYPE_TLD
from mantis.models.args_model import ArgsModel
from mantis.utils.crud_utils import CrudUtils
from mantis.utils.login_detector import LoginDetector

'''
LoginPageScanner module scans active subdomains, hosts, and paths for exposed login interfaces,
password inputs, and authentication endpoints.
Output: Findings of type informational
Information inserted in DB:
- host / url
- title: Exposed Login Page / Authentication Surface Detected
- description: Details of detected login surface, password fields, indicators
- severity: info
- type: informational
'''

class LoginPageScanner(APIScanner):

    DEFAULT_AUTH_PATHS = [
        "",
        "/login",
        "/signin",
        "/admin",
        "/auth",
        "/dashboard",
        "/portal",
        "/user/login",
        "/api/v1/auth"
    ]

    async def get_api_calls(self, args: ArgsModel):
        self.asset_api_list = []
        self.scannerName = type(self).__name__
        self.org = args.org

        # Fetch subdomains and active hosts
        subdomains = await get_assets_grouped_by_type(self, args, ASSET_TYPE_SUBDOMAIN)
        active_assets = await get_assets_with_non_empty_fields(self, args, "active_hosts")

        hosts_to_scan = set()

        if subdomains:
            for sub in subdomains:
                hosts_to_scan.add(f"https://{sub}")
                hosts_to_scan.add(f"http://{sub}")

        if active_assets:
            for item in active_assets:
                if "active_hosts" in item and item["active_hosts"]:
                    for host_list in item["active_hosts"]:
                        for host in host_list:
                            if host.startswith("http://") or host.startswith("https://"):
                                hosts_to_scan.add(host)
                            else:
                                hosts_to_scan.add(f"https://{host}")

        for base_url in hosts_to_scan:
            base_url = base_url.rstrip("/")
            for path in self.DEFAULT_AUTH_PATHS:
                target_url = f"{base_url}{path}"
                self.asset_api_list.append((target_url, None, None, base_url))

        return [(self, "GET")]

    def parse_response(self, response):
        findings = []
        self.finding_type = "informational"

        if response and response.status_code in range(200, 399):
            url = response.url if hasattr(response, 'url') else ""
            html_content = response.text if hasattr(response, 'text') else ""

            login_finding = LoginDetector.detect_login_surface(
                url=url,
                html_body=html_content,
                status_code=response.status_code
            )

            if login_finding:
                finding_dict = {
                    "title": login_finding["title"],
                    "type": self.finding_type,
                    "severity": login_finding["severity"],
                    "description": login_finding["description"],
                    "url": url,
                    "org": self.org,
                    "info": {
                        "indicators": login_finding.get("indicators", []),
                        "confidence": login_finding.get("confidence", "LOW"),
                        "has_password_field": login_finding.get("has_password_field", False)
                    },
                    "others": {
                        "status_code": response.status_code
                    }
                }
                findings.append(finding_dict)

        return findings

    async def db_operations(self, output_dict, asset=None):
        if output_dict:
            await CrudUtils.insert_findings(self, asset, output_dict, self.finding_type)
