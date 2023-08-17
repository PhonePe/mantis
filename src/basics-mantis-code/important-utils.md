# Important Utils Function
---

Mantis stores the scan results in a MongoDB database. Therefore, when integrating a new scanner, you will also need to query/push data to/from MongoDB. 

To make this process easier, we have developed utility functions that interact with the database, keeping your new scanner integration simple..

The **tool_utils.py** under mantis/utils consists of functions that will help you fetch information required for your new scanner as well help you push the data into mongoDB.


## Read Data

### Get Basic Assets Data

When you are integrating a new scanner, in the context of recon automation, your will need to pass one of the inputs to your new scanner:

- Top Level Domains (TLDs)
- IPs
- Sub Domains

> **Location**: mantis/utils/tool_utils  
> **Function Name**: async def get_assets_grouped_by_type(args, asset_type)  
---  
> **Get TLDs**: self.assets = await get_assets_grouped_by_type(args, "TLD")  
> **Get Subdomains**: self.assets = await get_assets_grouped_by_type(args, "subdomains")  
> **Get IPs**: self.assets = await get_assets_grouped_by_type(args, "ip")

Thats it, its that simple !!

### Insert Data

Again, when you are integrating a new scanner, once the scan is complete, you will need insert the results into mongodb database

> **Location**: mantis/utils/crud_utils  

---  
> **Insert Assets**: async def insert_assets(assets: list, source='external')  
> **Update Assets**: async def update_asset(asset: str, org: str, tool_output_dict: dict):  
> **Insert Findings**: async def insert_findings(obj, asset: str, findings: list): 

> ⏭️ Now that we are aware about utility functions that will make data insertion and extration simpler. Let's now take a quick look at the database Models for Assets and Findings.