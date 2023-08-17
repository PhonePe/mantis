from pydantic import BaseModel, Field, validator
from typing import List, Optional

class DBConfig(BaseModel):
    mongoConnectionString: str


class ReportOutputConfig(BaseModel):
    outputFolder: str


class Module(BaseModel):
    moduleName: str
    tools: list
    order: int


class Workflow(BaseModel):
    workflowName: str = Field(regex='[a-zA-Z0-9_-]*$')
    schedule: str
    cmd: List[str]
    workflowConfig : List[Module]


class Notify(BaseModel):
    teamName: str
    scanEfficiency: bool
    channel: dict
    app: list
    assets: Optional[list] = Field(None)
    findings: Optional[list] = Field(None)

    # This function will check for the channel types that are integrated in Mantis. 
    @validator('channel')
    def check_channel(cls, v):
        valid_channels = ['slack']
        for key in v.keys():
            if key not in valid_channels:
                raise ValueError("Invalid channel Name specified. Please only select amongst following options: ", valid_channels)
        return v


class NucleiTemplate(BaseModel):
    whitelist: str = Field(None)
    blacklist: str = Field(None)

class AppConfig(BaseModel):
    workflow: List[Workflow]
    dbConfig: DBConfig
    logging: dict
    notify: List[Notify]
    app: dict
    nuclei_template_path: NucleiTemplate
 