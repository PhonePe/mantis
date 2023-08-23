import json
import os
import logging
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD

class JSONConverter:
    
    @staticmethod
    async def convert_to_json_array(args, path):

        domains = await get_assets_grouped_by_type(args, ASSET_TYPE_TLD)

        for domain in domains:
            input_file = os.path.join(path, domain, domain)
            output_file = os.path.join(path, domain, "output.json")

            logging.debug(f"Processing domain: {domain}")

            try:
                with open(input_file, 'r') as f:
                    lines = f.readlines()

                data = []
                for line in lines:
                    json_obj = json.loads(line)
                    data.append(json_obj)

                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)

                logging.debug(f"Domain {domain} processed successfully.")

                # Delete the {domain} file
                os.remove(input_file)
                logging.debug(f"{domain} file deleted.")

            except FileNotFoundError:
                logging.error(f"Input file not found for domain: {domain}")
            except Exception as e:
                logging.error(f"Error processing domain {domain}: {e}")
