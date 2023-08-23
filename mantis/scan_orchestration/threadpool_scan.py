import time
import logging
import asyncio
from datetime import timedelta
from mantis.utils.common_utils import CommonUtils
from mantis.models.tool_logs_model import AssetLogs
    
class ExecuteScanThreadPool:
    
    async def execute_and_store(self,tool_tuple):
        
        tool_start_time = time.perf_counter()
        scanner = tool_tuple[0] 
        logging.debug(f"Executing command for {type(scanner).__name__}")
        results = await scanner.execute(tool_tuple)
        if results == None:
            logging.warning(f"No scan efficiency matrix returned, scan efficiency for {type(scanner).__name__} will be hampered")
        else:
            results["tool_name"] = type(scanner).__name__
            tool_end_time = time.perf_counter()
            tool_time_taken = str(timedelta(seconds=round(tool_end_time - tool_start_time, 0)))
            results["tool_time_taken"] = tool_time_taken
            asset_log = AssetLogs(**results)
        return asset_log




        