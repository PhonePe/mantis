from pydantic import BaseModel, Field
from typing import Literal, Optional


class Assets(BaseModel):

    _id: str = Field(..., alias="_id")
    asset: str = Field(...)
    asset_type: str = Field(...) ## type literal simlar domains. 
    org: str = Field(...)
    app: str = Field(None)
    source: Literal['internal', 'external'] = Field(None) 
    created_timestamp: str = Field(None)
    cdn_names: Optional[str] = list()
    waf: Optional[str] = list()
    ports: Optional[list] = list()
    as_number: Optional[str] = Field(None) # can have asn_number, name
    as_name: Optional[str] = Field(None)
    as_country: Optional[str] = Field(None)
    as_range: Optional[list] = list()
    dns: Optional[dict] = Field(None) # A, AAA, CNAME records - 
    ipinfo: Optional[dict] = dict()
    technologies: Optional[list] = list()
    webserver: Optional[list] = list()
    updated_timestamp: Optional[str] = Field(None)
    active_hosts: Optional[list] = list()
    stale: Optional[bool] = False
    repositories: Optional[str] = Field(None)
    tools_source: Optional[str] = Field(None)
    others: Optional[dict] = dict()


## Mandate out the fields which are not compulsorily required for every type of finding. 
class Findings(BaseModel):

    _id: str = Field(...)
    host: str = Field(...) #
    url: Optional[str] = Field(None) #
    title: str = Field(...) #
    org: str = Field(...) 
    app: str = Field(None)
    type: Literal['vulnerability', 'misconfiguration', 'secret', 'phishing', 'informational'] = Field(None) #
    description: str = Field(None)
    severity: str = Field(None)
    tool_source: str = Field(None) #
    created_timestamp: str = Field(None)
    updated_timestamp: Optional[str] = Field(None)
    host_with_protocol: Optional[str] = Field(None)
    remediation: Optional[str] = Field(None)
    info: Optional[dict] = Field(None) #
    cve_id: Optional[str] = Field(None)
    cwe_id: Optional[str] = Field(None)
    others: Optional[dict] = Field(None) #
    falsepositive: bool = Field(None)
    status: str = "Open"
    modified_by: str = Field(None)


class Extended(BaseModel):
    _id: str = Field(..., alias="_id")
    asset: str = Field(...)
    url: str = Field(...)
    asset_type: str = Field(...)
    org: str = Field(...)
    is_verified: Optional[Literal['verified', 'not_verified']] = Field(None)
    availability_status: Optional[Literal['Exists', 'Not Exists']] = Field(None)
    created_timestamp: str = Field(None)
    updated_timestamp: Optional[str] = Field(None)
    others: Optional[dict] = dict()