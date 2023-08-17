from pydantic import BaseModel, Field
from typing import Union, List

class AssetLogs(BaseModel):
    tool_name: str 
    success: int = 0
    failure: int = 0
    code: int = Field(None)
    command: Union[str, list] = Field(None)
    errors: str = Field(None)
    exception: str = Field(None)
    tool_time_taken: str = Field(None)
    output: str = Field(None)
    

class ModuleLogs(BaseModel):
    module_name: str
    module_start_time: str
    module_end_time: str
    module_time_taken: str
    module_tool_logs: List[AssetLogs] = Field(None)


class ScanLogs(BaseModel):
    scan_start_time: str
    scan_end_time: str
    scan_time_taken: str
    scan_modules_logs: List[ModuleLogs]
    