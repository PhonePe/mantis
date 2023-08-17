import os
import re
import yaml
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD

class URLDownloader:
    file_path = None
    extensions = ['js', 'xml']

    @staticmethod
    def create_folders(base_path, extensions):
        for extension in extensions:
            folder_path = os.path.join(base_path, extension)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)


    @staticmethod
    def download_file(url, extension, base_path):
        try:
            logging.info(f"Downloading {url}")
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading {url}: {e}")
        else:
            if response.status_code == 200:
                with open(os.path.join(base_path, extension, os.path.basename(url)), 'wb') as f:
                    f.write(response.content)
                    logging.info(f"Downloaded: {url}")


    @staticmethod
    def find_links_in_file():
        url_pattern = re.compile(r'"url":"(https?://[^"]+)"')
        urls = []

        try:
            with open(URLDownloader.file_path, 'r') as file:
                for line in file:
                    match = url_pattern.search(line)
                    if match:
                        urls.append(match.group(1))

            return urls

        except FileNotFoundError:
            logging.error("File not found!")
            return None


    @staticmethod
    async def process_urls(args, path):
        domains = await get_assets_grouped_by_type(args, ASSET_TYPE_TLD)
        for domain in domains:
            domain = domain.strip()
            URLDownloader.file_path = f"{path}/{domain}/{domain}"
            logging.info(f"{URLDownloader.file_path} File not found!")

        if URLDownloader.extensions:
            base_path = os.path.join(path, domain)
            URLDownloader.create_folders(base_path, URLDownloader.extensions)

            found_urls = URLDownloader.find_links_in_file()

            if found_urls:
                with ThreadPoolExecutor(max_workers=5) as executor:
                    for url in found_urls:
                        for extension in URLDownloader.extensions:
                            if url.endswith(extension):
                                executor.submit(URLDownloader.download_file, url, extension, base_path)
                                break
            else:
                logging.info("No URLs found in the file.")
        else:
            logging.info("No extensions found in the config file.")
