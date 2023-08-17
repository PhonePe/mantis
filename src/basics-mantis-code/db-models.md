# DB Models
---

One more thing you need to understand before integrating your new scanner is the database models. Mantis's mongoDB database consists of two collections (or tables).

- Assets (Types: TLDs, IPs, Subdomains, Certificates)
- Findngs (Types: Vulnerability, Misconfiguration, Secrets, Phishing Domain)

## Assets:

```python
    _id: str = Field(..., alias="_id")
    asset: str = Field(...)
    asset_type: str = Field(...) 
    org: str = Field(...)
    app: str = Field(None)
    source: Literal['internal', 'external'] = Field(None) 
    created_timestamp: str = Field(None)
    cdn_names: Optional[str] = list()
    waf: Optional[str] = list()
    ports: Optional[list] = list()
    as_number: Optional[str] = Field(None) 
    as_name: Optional[str] = Field(None)
    as_country: Optional[str] = Field(None)
    as_range: Optional[list] = list()
    dns: Optional[dict] = Field(None)
    ipinfo: Optional[dict] = dict()
    technologies: Optional[list] = list()
    webserver: Optional[list] = list()
    updated_timestamp: Optional[str] = Field(None)
    active_hosts: Optional[list] = list()
    stale: Optional[bool] = False
    repositories: Optional[str] = Field(None) 
    others: Optional[dict] = dict()
```

## Findings:

```python
    _id: str = Field(...)
    host: str = Field(...) 
    url: Optional[str] = Field(None) 
    title: str = Field(...) 
    org: str = Field(...) 
    app: str = Field(None)
    type: Literal['vulnerability', 'misconfiguration', 'secret', 'phishing'] = Field(None) 
    description: str = Field(None)
    severity: str = Field(None)
    tool_source: str = Field(None) 
    created_timestamp: str = Field(None)
    updated_timestamp: Optional[str] = Field(None)
    host_with_protocol: Optional[str] = Field(None)
    remediation: Optional[str] = Field(None)
    info: Optional[dict] = Field(None) 
    cve_id: Optional[str] = Field(None)
    cwe_id: Optional[str] = Field(None)
    others: Optional[dict] = Field(None) 
    falsepositive: bool = Field(None)
    status: str = "Open"
    modified_by: str = Field(None)


```