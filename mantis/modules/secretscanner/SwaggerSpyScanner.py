import logging
import os
import re
import subprocess
import sys

from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.utils.crud_utils import CrudUtils
from mantis.constants import ASSET_TYPE_SUBDOMAIN

'''
SwaggerSpyScanner scans Swagger/OpenAPI documentation endpoints exposed on
discovered subdomains for accidentally leaked secrets (API keys, tokens,
passwords, credentials, etc.) using the SwaggerSpy tool.

Tool: https://github.com/UndeadSec/SwaggerSpy
Output: Findings inserted into the database as type "secret"
'''


class SwaggerSpyScanner(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        self.domains = await get_assets_grouped_by_type(self, args, ASSET_TYPE_SUBDOMAIN)
        return [(self, "SwaggerSpyScanner")]

    async def execute(self, tool_tuple):
        results = {"success": 0, "failure": 0}

        if not self.domains:
            logging.warning("SwaggerSpyScanner: No subdomains found to scan.")
            return results

        for domain in self.domains:
            try:
                logging.info(f"SwaggerSpyScanner: Scanning domain: {domain}")
                findings = await self._run_swaggerspy(domain)
                if findings:
                    await CrudUtils.insert_findings(
                        self,
                        domain,
                        findings,
                        "secret",
                        "host"
                    )
                    logging.info(f"SwaggerSpyScanner: Inserted {len(findings)} finding(s) for {domain}")
                else:
                    logging.info(f"SwaggerSpyScanner: No secrets found for {domain}")
                results["success"] += 1
            except Exception as e:
                logging.error(f"SwaggerSpyScanner: Error scanning {domain}: {e}")
                results["failure"] += 1
                results["exception"] = str(e)

        return results

    async def _run_swaggerspy(self, domain: str) -> list:
        '''
        Runs SwaggerSpy against the given domain and returns a list of
        finding dicts ready for insertion via CrudUtils.insert_findings().
        '''
        try:
            env = {**os.environ, "NO_COLOR": "1"}
            proc = subprocess.run(
                ["swaggerspy", domain],
                capture_output=True,
                text=True,
                env=env,
                timeout=120
            )
            output = proc.stdout + proc.stderr
            logging.debug(f"SwaggerSpyScanner raw output for {domain}:\n{output}")
        except FileNotFoundError:
            logging.error(
                "SwaggerSpyScanner: 'swaggerspy' command not found. "
                "Install it with: pip install git+https://github.com/UndeadSec/SwaggerSpy.git"
            )
            raise
        except subprocess.TimeoutExpired:
            logging.error(f"SwaggerSpyScanner: SwaggerSpy timed out for domain: {domain}")
            raise

        return self._parse_output(output, domain)

    def _parse_output(self, output: str, domain: str) -> list:
        '''
        Parses SwaggerSpy plain-text output and converts matches into
        finding dicts compatible with CrudUtils.insert_findings().

        SwaggerSpy prints found secrets as lines containing the pattern name
        and the matched value, e.g.:
            [API_KEY] abc123xyz
            [AWS_SECRET] wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
        '''
        finding_dict_list = []

        # Strip ANSI escape codes in case NO_COLOR was not honoured
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_output = ansi_escape.sub('', output)

        # Match lines like: [RULE_NAME] matched_value
        secret_pattern = re.compile(r'\[([^\]]+)\]\s+(.+)')

        for line in clean_output.splitlines():
            line = line.strip()
            if not line:
                continue
            match = secret_pattern.match(line)
            if match:
                rule_id = match.group(1).strip()
                secret_value = match.group(2).strip()

                finding_dict = {
                    "host": domain,
                    "url": f"https://{domain}",
                    "title": "Swagger/OpenAPI Secret Leak",
                    "org": self.args.org,
                    "type": "secret",
                    "info": {
                        "key": secret_value,
                        "RuleID": rule_id,
                        "Match": secret_value,
                        "Entropy": "",
                        "source": "SwaggerSpy"
                    },
                    "others": {}
                }
                finding_dict_list.append(finding_dict)

        return finding_dict_list
