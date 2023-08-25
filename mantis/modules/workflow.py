'''
1. Read config of tools and workflow order
2. Load above classes dynamically
3. Workflow - Folder to load classes in that workflow. 
'''
import os
import sys
import time
import json
import logging
import asyncio
import importlib
from tqdm import tqdm
from datetime import timedelta
from mantis.modules.alerter import Alerter
from mantis.utils.config_utils import ConfigUtils
from mantis.utils.list_assets import ListAssets
from mantis.models.args_model import ArgsModel
from mantis.utils.asset_type import AssetType
from mantis.utils.crud_utils import CrudUtils
from mantis.utils.common_utils import CommonUtils
from mantis.utils.tool_utils import get_assets_grouped_by_type
from mantis.constants import ASSET_TYPE_TLD, ASSET_TYPE_SUBDOMAIN, ASSET_TYPE_IP
from mantis.scan_orchestration.threadpool_scan import ExecuteScanThreadPool
from mantis.models.tool_logs_model import ModuleLogs, ScanLogs

logging.getLogger().setLevel(logging.INFO)
class Workflow:

    
    @staticmethod
    def get_all_classes(module):
        tool_classes = []
        logging.debug(f'Fetching classes for the module {module}')

        try:
            for tool in module.tools:
                
                curr_package = sys.modules[__name__].__package__ + "." + module.moduleName          
                mod = importlib.import_module(curr_package + "." +tool)
                tool_class = getattr(mod, tool)
                tool_classes.append(tool_class)
                        
        except Exception as e:
            logging.error(f"Error fetching classes for tool - {tool}: {e}")

        logging.debug(f'Tool classes fetched - {tool_classes}')

        return tool_classes

                    
    async def workflow_executor(args: ArgsModel):
        logs = []
        workflow = ConfigUtils.get_module_dict(args.workflow)
        logging.info(f"Executing workname {workflow}")
        if args.input:
            list_assets = ListAssets.list_assets(args=args)
            assets_with_type = AssetType.assign_asset_type(assets=list_assets, args=args)
            asset_dict_list = CrudUtils.create_assets_dict(args, assets_with_type=assets_with_type)

            logging.info("Inserting user input into database")
            await CrudUtils.insert_assets(assets=asset_dict_list, source='internal')
        
        tld_assets = await get_assets_grouped_by_type(args, ASSET_TYPE_TLD)
        subdomain_assets = await get_assets_grouped_by_type(args, ASSET_TYPE_SUBDOMAIN)
        ip_assets = await get_assets_grouped_by_type(args, ASSET_TYPE_IP)

       
        if len(tld_assets) == 0 and len(subdomain_assets) == 0 and len(ip_assets) == 0:
            logging.error("No input available for tools. Quitting!!")
            sys.exit(1)
        
        
        ordered_modules = ConfigUtils.get_ordered_module_list(workflow=workflow)
        
        scan_stat = {}
        scan_stat['scan_start_time'] = CommonUtils.get_ikaros_std_timestamp()
        scan_start_time = time.perf_counter()
        scan_stat['scan_modules_logs'] = []

        print()

        for module in ordered_modules:
            module_log = {}
            module_log["module_name"] = module.upper()
            module_log["module_start_time"] = time.perf_counter()
            commands_list = []
            # This parameter controls the number of processes
            # This returns all the tool classes for a module
            module_classes = Workflow.get_all_classes(ConfigUtils.get_module(module_name=module, workflow=workflow))
            logging.debug(f"Tool classes for {module} is {module_classes}")
            try:
                for _class in module_classes:
                    try:
                        logging.debug(f"Calling base function for {_class.__name__}")
                        class_object = _class()
                    
                        logging.debug(f"class object for {_class}: {class_object}")
                        tool_command_list = await class_object.init(args)
                        commands_list.extend(tool_command_list)
                        logging.debug(f"Command list for {_class.__name__} : {tool_command_list}")
                    except Exception as e:
                        logging.error(f"Something went wrong in {_class.__name__} : {e}")

                if args.use_ray:
                    from mantis.scan_orchestration.ray_scan import ExecuteRayScan
                    import ray
                    num_actors = args.num_actors
                    num_actors = min(num_actors, len(commands_list))
                    futures_res = []
                    executeScanActors = [ExecuteRayScan.remote() for i in range(num_actors)]
                    futures = [executeScanActors[i%num_actors].execute_and_store.remote(commands_list[i]) for i in range(len(commands_list))]
                    with tqdm(total=len(commands_list), desc=module.upper()) as pbar:
                        while futures:

                            ready, futures = ray.wait(futures)

                            for objRef in ready:
                                futures_res.append(ray.get(objRef))
                                pbar.update(1)
                    
                    logging.info(f"Awaiting for the results of tool execution")
                    module_log["module_tool_logs"] = futures_res
                
                else:
                    execute_threadpool_obj = ExecuteScanThreadPool()
                    def done_callback(future):
                        
                        pbar.update(1)
                    loop = asyncio.get_running_loop()
                    tasks = []
                    with tqdm(total=len(commands_list), colour="green") as pbar:
                        for tool_tuple in commands_list:
                            pbar.set_description(module.upper())
                            task = loop.create_task(execute_threadpool_obj.execute_and_store(tool_tuple))
                            tasks.append(task)
                            task.add_done_callback(done_callback)
                        res = await asyncio.gather(*tasks)
                    
                    module_log["module_tool_logs"] = res

            except FileNotFoundError as e:
                logging.debug("No file generated for tool")
            except Exception as e:
                logging.error(f"Error calling core functions on tool classes {e}")

            print()

            module_log["module_end_time"] = time.perf_counter()
            module_log["module_time_taken"] = str(timedelta(seconds=round(module_log["module_end_time"] - module_log["module_start_time"], 0)))
            moduleLog_validated = ModuleLogs(**module_log)
            scan_stat["scan_modules_logs"].append(moduleLog_validated)

        scan_end_time = time.perf_counter()
        scan_stat['scan_end_time'] = CommonUtils.get_ikaros_std_timestamp()
        scan_stat['scan_time_taken'] = str(timedelta(seconds=round(scan_end_time - scan_start_time, 0)))
        scan_stat_validated = ScanLogs(**scan_stat)

        logs = json.dumps(ScanLogs.parse_obj(scan_stat_validated).dict()) 

        if args.delete_logs:
            logging.info("Cleaning up logs folder")
            log_dir = 'logs/scan_efficiency'
            if os.path.exists(log_dir):
                for log in os.listdir(log_dir):
                    os.remove(os.path.join(log_dir, log))
            log_dir = 'logs/tool_logs'
            if os.path.exists(log_dir):
                for log in os.listdir(log_dir):
                    os.remove(os.path.join(log_dir, log))

        if not os.path.exists('logs/scan_efficiency'):
            os.makedirs('logs/scan_efficiency')
        logfile_name = 'logs/scan_efficiency/'+ args.org + str(time.time()).split('.')[0] + "-logs.json"

        with open(logfile_name, "w", encoding="utf-8") as outfile:
            outfile.write(str(logs))

        scan_stats, module_scan_stats = await Alerter.send_alerts(log_dict=scan_stat_validated, args=args)
        module_stats = ""
        # print(module_scan_stats)
        for module in module_scan_stats:
            module_stats += "\033[1;34m"+module["module_name"] + "\033[0m\n"
            module_stats += f"Time taken: {module['module_time_taken']}\n"
            module_stats += f"Efficiency: {module['module_efficiency']}\n\n"
        print(f'''\u001B[32m
\033[1;32mSCAN STATS:\033[0m
              
\033[1;34mTOTAL\033[0m
Efficiency: {scan_stats['scan_percentage']}
Time taken: {scan_stats['scan_time_taken']}

{module_stats}
You can find the detailed stats for each tool/subdomain combination here: {logfile_name}

\033[1;32mScan Completed

\u001B[0m''')
        
