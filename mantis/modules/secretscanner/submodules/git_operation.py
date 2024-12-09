import json
import os,sys
import re
import yaml
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from mantis.utils.base_request import BaseRequestExecutor
from mantis.modules.secretscanner.submodules.secret_finder import SecretFinder
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD
from subprocess import Popen
from mantis.modules.secretscanner.submodules.gitleaks_runner import GitleaksRunner
from mantis.modules.secretscanner.submodules.url_downloader import URLDownloader
from mantis.config_parsers.config_client import ConfigProvider
from mantis.db.crud_vulnerabilities import check_field_exists
from mantis.utils.crud_utils import CrudUtils
from pathlib import Path
from git import repo
import git
import shutil
import time
import os
import subprocess

class GitOperation:

    def __init__(self,args,method):
        self.args = args
        self.method = method
        self.github_api_host = ConfigProvider.get_config().github_config.host
        self.tokens = ConfigProvider.get_config().github_config.tokens
        self.token_index = 0
        self.token = self.tokens[self.token_index]
        # self.headers = {'User-Agent': 'curl/7.64.1', 'Authorization': f'Basic {self.token}'}
        self.download_path = ConfigProvider.get_config().github_config.download_location
        self.extended_assets = "Extended Assets"


    def create_dir(self):
        path = ConfigProvider.get_config().github_config.download_location

        repo_path = f"{path}"
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            logging.info(f"{repo_path} is deleted")
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            logging.error(f"Error creating directory {path}: {e.strerror}")



    async def org_scan(self):
        self.create_dir()
        org = self.args.org
        method = self.method
        page = 1
        results = {"success": 0, "failure": 0}

        logging.info(f"Started crawling for org: {org}")

        while True:
            try:
                logging.info(f"Using GitHub token index: {self.token_index}")
                github_url = f"{self.github_api_host}/orgs/{org}/repos?page={page}"
                request_tuple = (github_url, self.get_headers(), None, None)

                _, response = BaseRequestExecutor.sendRequest("GET", request_tuple)
                if response.status_code == 403:
                    self.switch_token()
                    continue

                if response.status_code != 200:
                    logging.error(f"Unexpected response code: {response.status_code}")
                    break

                repo_data = json.loads(response.text)
                if not repo_data:  # Stop if no more repos on the current page
                    logging.info("No more results found")
                    break

                logging.info(f"Processing {len(repo_data)} repositories on page {page}")
                await self.process_repositories(repo_data, None,results)

                page += 1
                time.sleep(5)  # Respect API rate limits

            except Exception as e:
                logging.error(f"Error during crawling: {str(e)}")
                break

        return results

    async def public_scan(self, domains):
        for domain in domains:
            page = 1
            results = {"success": 0, "failure": 0}
            logging.info(f"Started crawling for domain: {domain}")

            while True:
                try:
                    logging.info(f"Crawling page {page} with token index {self.token_index}")
                    github_url = f"{self.github_api_host}/search/code?q={domain}&page={page}"
                    request_tuple = (github_url,{'User-Agent': 'curl/7.64.1', 'Authorization': f'Basic {self.token}'}, None, None)

                    _, response = BaseRequestExecutor.sendRequest("GET", request_tuple)

                    if response.status_code == 403:  # Rate limit hit, switch token
                        self.switch_token()
                        logging.info("Rate limit Occurred, sleeping for 10 sec ")
                        time.sleep(10)
                        continue

                    if response.status_code != 200:
                        logging.error(f"Unexpected response code: {response.status_code}")
                        break

                    code_results = json.loads(response.text)
                    if not code_results.get('items'):  # Break if no more results
                        logging.info(f"No more results for domain {domain} on page {page}")
                        logging.info("Sleeping for 10 sec to avoid rate limit")
                        time.sleep(10)
                        break

                    logging.info(f"Found {len(code_results['items'])} results for domain {domain}")
                    await self.process_repositories(code_results['items'], domain, results)
                    page += 1  # Move to the next page
                    time.sleep(5)  # Respect GitHub's rate limits

                except Exception as e:
                    logging.error(f"An error occurred during crawling for domain {domain}: {str(e)}")
                    break  # Exit on any unexpected error

        return results



    async def process_repositories(self, repo_data, domain, results):
        """Process each repository, whether from search results or directly via cloning."""
        for index, repo in enumerate(repo_data):
            # Extract repository and owner information
            repo_url = repo.get('repository', {}).get('html_url', repo.get('html_url'))
            repo_name = repo.get('repository', {}).get('name', repo.get('name'))
            raw_url = repo.get('url')
            github_url = repo.get('html_url')
            profile_url = repo.get('repository', {}).get('owner', {}).get('html_url', '')

            github_info = {
                "Github Url": github_url,
                "Repo Url": repo_url,
                "Repo Name": repo_name,
                "Raw Github Url": raw_url,
                "Profile Url": profile_url
            }

            try:
                logging.info(f"Processing repository {index + 1}: {repo_name}")

                # Check if the repository has already been processed
                existing_url = await check_field_exists("info.github_source.Raw Url", raw_url)
                if existing_url:
                    logging.info(f"{raw_url} is already present in the database")
                    continue

                logging.info("Raw URL not present in the database. Proceeding with processing.")

                #Extended Asset
                extended_dict_list = []
                extended_assets_dict = {}

                if "org" == self.method:
                    extended_assets_dict["_id"] = repo_url
                    extended_assets_dict["url"] = repo_url
                    extended_assets_dict["asset"] = repo_url
                    extended_assets_dict["asset_type"] = f"Github Repo - Org Scan"
                    extended_assets_dict["org"] = self.args.org

                    # Clone the repository and download any raw files if necessary
                    repo_path = GitOperation.clone_repo(repo_url)


                if "public" in self.method:
                    extended_assets_dict["_id"] = github_url
                    extended_assets_dict["url"] = github_url
                    extended_assets_dict["asset"] = domain
                    extended_assets_dict["asset_type"] = f"Github Repo - Public Scan"
                    extended_assets_dict["org"] = self.args.org

                    # process the github URL
                    repo_path = await self.process_github_urls(raw_url, domain, repo_name)

                # Process the repository with gitleaks
                GitleaksRunner.process_repos(repo_name, self.download_path)

                extended_dict_list.append(extended_assets_dict)
                if len(extended_dict_list):
                    await CrudUtils.insert_extended_assets(extended_dict_list)

                # Run the secret finding process
                secret_finder = SecretFinder(repo_name, self.args, self.download_path)
                await secret_finder.find_secrets_in_repos(github_info,domain)

                logging.info(f"Sleeping for 10 sec to avoid Rate limit")
                time.sleep(10)

                results["success"] += 1

                # Cleanup by deleting the cloned repository folder
                logging.debug(f"Deleting repository folder: {repo_path}")
                shutil.rmtree(repo_path)

            except Exception as e:
                logging.error(f"Error processing repository {repo_name}: {str(e)}")
                results["failure"] += 1

    def switch_token(self):
        """Switches to the next token when rate limit is hit."""
        self.token_index = (self.token_index + 1) % len(self.tokens)
        self.token = self.tokens[self.token_index]
        logging.info(f"Switched to GitHub token index: {self.token_index} with token: {self.token}")

    def get_headers(self):
        """Return updated headers with the current token."""
        return {'User-Agent': 'curl/7.64.1', 'Authorization': f'Basic {self.token}'}

    @staticmethod
    def clone_repo(repo_url):
        destination_dir = ConfigProvider.get_config().github_config.download_location
        repo_name = repo_url.split('/')[-1]

        try:
            logging.info(f"Cloning {repo_url} into {destination_dir}")  # Moved from print to logging

            # Full path where the repository will be cloned
            clone_path = os.path.join(destination_dir, repo_name)

            # Run git clone command
            result = subprocess.run(["git", "clone", repo_url, clone_path], capture_output=True, text=True)

            if result.returncode == 0:
                logging.info(f"Successfully cloned {repo_url} into {clone_path}")
                return clone_path  # Return the exact path of the cloned repo
            else:
                logging.error(f"Failed to clone {repo_url}. Error: {result.stderr}")
                return None

        except Exception as e:  # Catching any exception during cloning
            logging.error(f"Error while cloning repo {repo_url} - {str(e)}")
            return None


    async def process_github_urls(self,url,domain,name):
        path = Path(ConfigProvider.get_config().github_config.download_location) / name  # Create a folder based on 'name'
        path.mkdir(parents=True, exist_ok=True)  # Create the folder if it doesn't exist

        logging.info(f"Starting download for {url} into folder: {name}")

        request_tuple = url, self.get_headers(), None, None
        _, response = BaseRequestExecutor.sendRequest("GET", request_tuple)

        if response.status_code == 403:
            logging.info(f"Rate Limit Triggered, Sleeping for 10 Sec")
            time.sleep(10)

        if response.status_code == 200:  # Ensure response is successful
            _response = json.loads(response.text)

            detailed_info_url = _response.get('download_url')

            # Send a request to the download URL
            download_tuple = detailed_info_url, None, None, None
            _, download_url_response = BaseRequestExecutor.sendRequest("GET", download_tuple)

            if download_url_response.status_code == 200:
                file_name = detailed_info_url.split("/")[-1]  # Extract the file name from the URL
                file_path = path / file_name  # Full path to save the file

                logging.info("File Downloading Started...")

                try:
                    with open(file_path, 'wb') as file:
                        file.write(download_url_response.content)  # Write the content to the file
                    logging.info(f"{file_name} download finished and saved at {file_path}")

                    logging.info(f"Sleeping to avoid Rate Limit")
                    time.sleep(5)

                    return path
                except Exception as e:
                    logging.error(f"Error writing file {file_name}: {e}")
            else:
                logging.error(f"Failed to download {url}. Status code: {response.status_code}")
