import re
import hashlib
import logging
from mantis.constants import ASSET_TYPE_CLOUD_BUCKET
from mantis.utils.crud_utils import CrudUtils
from mantis.tool_base_classes.toolScanner import ToolScanner
from mantis.models.args_model import ArgsModel

# Regex to strip ANSI escape codes from colorama output
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

# True positive patterns from inSp3ctor tool's check_response():
# Status 200: [*] Bucket/Object is public [http://...]
PUBLIC_BUCKET = re.compile(r'\[\*\]\s+\w+ is public \[(https?://[^\]]+)\]')
# Status 301: [>] Bucket/Object has a redirect [http://...] Redirected here - [...]
REDIRECT_BUCKET = re.compile(r'\[>\]\s+\w+ has a redirect \[(https?://[^\]]+)\]')

# Cloud provider patterns to identify bucket type from URL
CLOUD_PROVIDER_PATTERNS = {
    'amazonS3': re.compile(r'amazonaws\.com'),
    'azure': re.compile(r'blob\.core\.windows\.net'),
    'digitalocean': re.compile(r'digitaloceanspaces\.com'),
    'googlecloud': re.compile(r'storage\.googleapis\.com'),
}

'''
InSp3ctor is a targeted reconnaissance tool built for the discovery and enumeration of Amazon S3 storage buckets.
Output: CSV File
'''


def extract_bucket_url(line):

    match = (
        PUBLIC_BUCKET.search(line) or
        REDIRECT_BUCKET.search(line)
    )
    if match:
        return match.group(1)
    return None


def identify_cloud_provider(url):
    """
    Identifies the cloud provider from the bucket URL.
    """
    for provider, pattern in CLOUD_PROVIDER_PATTERNS.items():
        if pattern.search(url):
            return provider
    return 'unknown'


class InSp3ctor(ToolScanner):

    def __init__(self) -> None:
        super().__init__()

    async def get_commands(self, args: ArgsModel):
        self.org = args.org
        self.base_command = f"python mantis/custom_tools/inSp3ctor/inSp3ctor.py -n {self.org} -c > {{output_file_path}}"
        self.outfile_extension = ".txt"
        self.assets = [self.org]
        return super().base_get_commands(self.assets)

    def parse_report(self, outfile):
        logging.debug('Parsing InSp3ctor Report for cloud recon - Begins')
        output_dict_list = []
        InSp3ctor_output = open(outfile).readlines()
        for line in InSp3ctor_output:
            clean_line = ANSI_ESCAPE.sub('', line).strip()

            bucket_url = extract_bucket_url(clean_line)
            if not bucket_url:
                continue

            unique_hash = hashlib.md5(
                str(bucket_url).encode() + str(ASSET_TYPE_CLOUD_BUCKET).encode() + str(self.org).encode()
            ).hexdigest()
            domain_dict = {}
            domain_dict['_id'] = unique_hash
            domain_dict['asset'] = identify_cloud_provider(bucket_url)
            domain_dict['url'] = bucket_url
            domain_dict['asset_type'] = ASSET_TYPE_CLOUD_BUCKET
            domain_dict['org'] = self.org
            domain_dict['tools_source'] = 'InSp3ctor'
            output_dict_list.append(domain_dict)
        return output_dict_list

    async def db_operations(self, tool_output_dict, asset=None):
        await CrudUtils.insert_extended_assets(tool_output_dict)
