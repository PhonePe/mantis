import logging
from concurrent import futures
from mantis.utils.base_request import BaseRequestExecutor
from mantis.models.args_model import ArgsModel


class APIScanner:

    def __init__(self) -> None:
        self.scannerName = None
        self.endpoint =  None
        self.secrets =  None
        self.headers =  None
        self.num_threads = None
        self.assets = []
        self.body = None
        self.asset_api_list = []
    

    async def init(self, args: ArgsModel):
        return await self.get_api_calls(args)


    def get_api_calls(self, args: ArgsModel):
        raise NotImplementedError
    

    def parse_reponse(self, response):
        raise NotImplementedError
    

    async def db_operations(self, output_dict, asset=None):
        raise NotImplementedError
    

    async def execute(self, tool_tuple):
        results = {}
        results["success"] = 0
        results["failure"] = 0
        method = tool_tuple[1]
        try:
            with futures.ThreadPoolExecutor(max_workers=1) as executor:  
                responses = [executor.submit(BaseRequestExecutor.sendRequest, method,api_call_tuple) for api_call_tuple in self.asset_api_list]

                for response in futures.as_completed(responses):

                    if (response.result()[1].status_code == 200):
                        results["success"] += 1
                    else:
                        results["failure"] += 1
                        
                    asset_update_dict = self.parse_reponse(response.result()[1])
                    if len(response.result()[0]):
                        await self.db_operations(asset_update_dict, asset=response.result()[0]) 
        except Exception as e:
            results["exception"] = str(e)
            logging.error(f"Error in API: {e} : {type(self).__name__}")        
        return results
