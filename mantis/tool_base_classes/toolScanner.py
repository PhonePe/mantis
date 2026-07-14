from mantis.utils.base_request import BaseRequestExecutor
from mantis.utils.common_utils import CommonUtils
from subprocess import Popen, PIPE, DEVNULL
from mantis.models.args_model import ArgsModel
import logging
import sys
import time
import asyncio
import os
import requests

class ToolScanner:
    
    def __init__(self) -> None:
        self.org = None
        self.base_command = None
        self.outfile_extension = None
        self.commands_list = []
        self.assets = []
        self.std = sys.stdout


    async def init(self, args:ArgsModel):
        return await self.get_commands(args=args)
    

    def get_commands(self, args: ArgsModel):
        raise NotImplementedError


    def base_get_commands(self, assets) :
        ## Return the list of commands
        command_list = []
        for every_asset in assets:  
            domain = every_asset
            outfile = CommonUtils.generate_unique_output_file_name(domain, self.outfile_extension)
            command = self.base_command.format(input_domain = domain, output_file_path = outfile)
            command_list.append((self, command, outfile, every_asset))
        self.commands_list = command_list
        return command_list

    def download_required_file(self):
        # Define the download directory
        download_dir = "configs/resources/"
        os.makedirs(download_dir, exist_ok=True)

        # Define URLs and corresponding filenames
        files = {
            "https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt": "resolvers.txt", # https://github.com/trickest
            "https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt": "best-dns-wordlist.txt"  # https://www.assetnote.io/
        }

        for url, filename in files.items():
            file_path = os.path.join(download_dir, filename)

            try:
                print(f"Downloading {filename}...")
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise an error for bad status codes (4xx, 5xx)

                # Get the total file size from the headers
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0

                # Download the file in chunks
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # Filter out keep-alive chunks
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            # Print download progress
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                print(f"Downloaded {downloaded_size}/{total_size} bytes ({progress:.2f}%)", end="\r")

                print(f"\nDownloaded {filename} successfully.")

            except requests.exceptions.RequestException as e:
                print(f"Failed to download {filename}: {e}")
                # Optionally, delete the partially downloaded file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted partially downloaded file: {filename}")

    def parse_report(self, outfile):
        raise NotImplementedError
    

    async def db_operations(self, tool_output_dict, asset=None):
        raise NotImplementedError
    

    async def execute(self, tool_tuple):
        results = {}
        command, outfile, asset = tool_tuple[1:]
        logging.debug(f"Executing command - {command}")
        
        if self.std == "PIPE":
            stderr = PIPE
            stdout = PIPE
        else:
            stderr = sys.stderr
            stdout = sys.stdout

        code = 1
        try:
            start = time.perf_counter()

            subprocess_obj = await asyncio.create_subprocess_shell(
                command, stderr=DEVNULL, stdout=DEVNULL, shell=True) 
            code = await subprocess_obj.wait()
            output,errors = await subprocess_obj.communicate()

            finish = time.perf_counter()

            results["code"] = code
            results["output"] = output
            results["errors"] = errors
            results["asset"] = asset
            results["command"] = command
            results["success"] = 0
            results["failure"] = 0
            results["command_exec_time"] = round(finish - start, 2)
            logging.debug(f"Subprocess output - Code {code}, Errors {errors}")
            if code == 0: 
                results["success"] += 1
            else:
                results["failure"] += 1
            tool_results_dict = self.parse_report(outfile=outfile)
            results["tool_time_taken"] = CommonUtils.get_ikaros_std_timestamp()
            # if tool_results_dict:
            await self.db_operations(tool_results_dict, asset=asset)
        
        except FileNotFoundError as e:
            logging.debug(f"No file generated for the {asset}")

        except Exception as e:
            results["exception"] = str(e)
            logging.debug(
                f"Error received: {type(e).__name__}: {e} for {asset} in tool {type(self).__name__}")
      
        return results