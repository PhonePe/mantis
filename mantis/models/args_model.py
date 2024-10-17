from pydantic import BaseModel, Field
from typing import Literal

class ArgsModel(BaseModel):

    input_type: Literal['host', 'file'] = Field(None)
    input: str = Field(None)
    workflow: str = 'default'
    org: str = Field(None)
    output: str = Field(None)
    app: str = Field(None)
    passive: bool = False
    stale: bool = False
    aws_profiles: list = Field(None)
    ignore_stale: bool = False
    use_ray: bool = False
    num_actors: int = 3
    delete_logs: bool = False
    verbose: bool = False
    thread_count: int = 3
    subdomain: str = Field(None)
    list_: bool = False
    list_orgs: bool = False
    report_: bool = False
    in_scope: bool = False
    