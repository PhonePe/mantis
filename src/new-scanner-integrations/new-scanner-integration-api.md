# Add a new API scanner class
---

Let's now try adding an API scanner instead of a command line tool, for example, SSLMate to Discovery module.

As a first step to integrate a new scanner, answer the below questions:

- **Which module will this scanner be a part of?**
    - SSLMate is used to retreive all the certificates belonging to an organisation, hence this will be under Discovery module
- **Is this scanner a command line tool or API?**
    - SSLMate is an API based scanner
- **What will the tool output?**
    - SSLMate will list all certificates, their DNS Names, public key, SHA. The certificate has to be added to assets and the corresponding recon information has to be update
- **What is the report output format we are expecting to parse?** 
    - JSON Response
- **What is the input that the tool takes, meaning, TLDs, subdomains, IPs etc.?**
    - SSLMate takes TLDs as an input

Now that we have a clear understanding of the expected input and output from the tool, let's begin the process of creating the scanner class. As previously indicated [here](/./mantis/basics-mantis-code/scanner-base-class.md), we are required to implement three functions:

- get_api_calls()
- parse_reponse()
- db_operations()

## Creating the API Class

> Please Note - The name of the tool class should be the same as defined in the config file

Create a new file under `/mantis/mantis/modules/discovery/` and name it SSLMate.py

## Implementing get_api_calls()

This function needs to return the tool object and the HTTP method.

```python

async def get_api_calls(self, args: ArgsModel):
        self.asset_api_list = []
        self.scannerName = type(self).__name__
        self.endpoint = "https://api.certspotter.com/v1/issuances?domain={domain_name}&include_subdomains=true&expand=dns_names&expand=issuer&expand=revocation&expand=problem_reporting&expand=cert_der"
        self.body = ""
        self.org = args.org
        self.assets.extend(await get_assets_grouped_by_type(args, ASSET_TYPE_TLD))
        for every_asset in self.assets:
            endpoint = self.endpoint.format(domain_name=every_asset)
            self.asset_api_list.append((self, endpoint, None,  every_asset))
        return [(self, "GET")]
```

- **self.endpoint** is the full HTTP request to the API Scanner
- **self.body** is the HTTP request body
- **self.org** is the organisation passed in the arguments
- The for loop generats an HTTP request per TLD

## Implementing parse_response()

This function is required to parse what the API outputs and insert it into the database. In this context, a list of certificates and its contextual information is extrated and inserted into the database.

```python

def parse_reponse(self, response):
        output_dict_list = []
        response_json = response.json()
        for every_cert in response_json:
            cert_dict = {}
            cert_dict['asset'] = every_cert['id']
            cert_dict['asset_type'] = ASSET_TYPE_CERT
            cert_dict['org'] = self.org
            cert_dict['others'] = {}
            cert_dict['others']['dns_names'] = every_cert['dns_names']
            cert_dict['others']['tbs_sha256'] = every_cert['tbs_sha256']
            cert_dict['others']['cert_sha256'] = every_cert['cert_sha256']
            cert_dict['others']['pubkey_sha256'] = every_cert['pubkey_sha256']
            cert_dict['others']['issuer'] = every_cert['issuer']
            cert_dict['others']['not_before'] = every_cert['not_before']
            cert_dict['others']['not_after'] = every_cert['not_after']
            cert_dict['others']['revoked'] = every_cert['revoked']
            cert_dict['others']['revocation'] = every_cert['revocation']
            cert_dict['others']['cert_der'] = every_cert['cert_der']
            
            output_dict_list.append(cert_dict)

        return output_dict_list

```
> You dont have to worry about where the HTTP response is retrieved etc. The response parameter contains the HTTP Reponse

Extract the necessary information you want to store in the mongoDB, plus the org context and the type of Asset

## Implementing db_operations()

The final step is to insert the data into mongoDB

```python

    async def db_operations(self, output_dict, asset=None):
        await CrudUtils.insert_assets(output_dict)

```
This is straight forward, call the corresponding util function to insert the data into mongoDB.

> Info💡- Depending on whether you are inserting an asset, or updating an asset for recon information, or adding a new finding, you can use the corresponding util functions as described [here](/./mantis/basics-mantis-code/important-utils.md)

> Let's now look at adding the new scanner to the config file. 