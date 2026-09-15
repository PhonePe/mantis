# Mantis Cloud Inventory

Cloud Inventory collects cloud resources that may be exposed to the internet and stores them in the `cloud_assets` collection. The supported providers are AWS, Azure, and Cloudflare.

Cloud Inventory runs through the `cloudinventory` workflow. The dedicated workflow is enabled by default. Cloud Inventory in the `default` workflow is opt-in and remains disabled unless enabled in `configs/local.yml`.

## Before You Start

Complete the Mantis installation described in the main [README](README.md) before configuring Cloud Inventory. Run the commands below from the Mantis application directory, where `configs/local.yml` is located.

The organization supplied with `-o` must already exist and have assets in MongoDB. For a new organization, onboard an asset first:

```shell
mantis onboard -o org_name -t example.com
```
## Configure AWS

Create one named profile per AWS account in `configs/aws_credentials`:

```ini
[account-prod]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY

[account-staging]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

Configure the profile names and optional regions in `configs/local.yml`:

```yaml
aws:
  config_path: configs/aws_config
  credentials_path: configs/aws_credentials

cloud:
  aws:
    profiles:
      - account-prod
      - account-staging
    regions: []
```

An empty `regions` list discovers all regions returned by AWS. For static access keys, `credentials_path` is required and `config_path` is optional. Leave `config_path` empty when no AWS config file is needed:

```yaml
aws:
  config_path:
  credentials_path: configs/aws_credentials
```

### Optional AWS Config File

The optional `configs/aws_config` file is useful when profiles need settings beyond access keys, such as a default region, role assumption, SSO, or MFA-related profile configuration. Point to it from `local.yml`:

```yaml
aws:
  config_path: configs/aws_config
  credentials_path: configs/aws_credentials
```

For profile-specific regions or role assumption, use the AWS config-file format:

```ini
[profile account-prod]
region = us-east-1

[profile account-staging]
region = eu-west-1
```

For a role-based profile, add a source profile and role ARN:

```ini
[profile account-prod-readonly]
role_arn = arn:aws:iam::123456789012:role/ReadOnlyRole
source_profile = account-prod
region = us-east-1
```

For AWS SSO, configure the profile and its SSO session in this file, following the AWS CLI profile format. In these cases, the profile names in `cloud.aws.profiles` must match the names in the credentials/config files.

The AWS profiles must have permission to call the inventory APIs, such as STS, EC2, ELB, RDS, and S3. Use read-only credentials and never commit real credentials to the repository.

The `-aws` option can select profiles for a scan:

```shell
mantis scan -o org_name -w cloudinventory -aws account-prod,account-staging
```

When `cloud.aws.profiles` is populated in `local.yml`, those profiles are used for the Cloud Inventory scan. Each profile should represent one AWS account.

## Configure Azure

Use a Microsoft Entra service principal in `configs/local.yml`:

```yaml
cloud:
  azure:
    tenant_id: YOUR_TENANT_ID
    client_id: YOUR_CLIENT_ID
    client_secret: YOUR_CLIENT_SECRET
    subscription_ids: []
```

An empty `subscription_ids` list scans all subscriptions accessible to the service principal. To restrict the scan, list subscription IDs explicitly.

Azure credentials can also be supplied through environment variables:

```shell
export AZURE_TENANT_ID="YOUR_TENANT_ID"
export AZURE_CLIENT_ID="YOUR_CLIENT_ID"
export AZURE_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

## Configure Cloudflare

An API token is recommended:

```yaml
cloud:
  cloudflare:
    api_token: YOUR_API_TOKEN
```

Or use:

```shell
export CF_API_TOKEN="YOUR_API_TOKEN"
```

Email and global API key authentication is also supported:

```yaml
cloud:
  cloudflare:
    email: user@example.com
    api_key: YOUR_GLOBAL_API_KEY
```

Or use:

```shell
export CF_API_EMAIL="user@example.com"
export CF_API_KEY="YOUR_GLOBAL_API_KEY"
```

API token authentication takes priority when both methods are configured. Use a token with the minimum required read permissions where possible.

## Run Combined Cloud Inventory

The dedicated workflow runs every provider listed in its `tools` configuration:

```shell
mantis scan -o org_name -w cloudinventory
```

For AWS, pass one or more profile names as a comma-separated list:

```shell
mantis scan -o org_name -w cloudinventory -aws account-prod,account-staging
```

Providers without valid credentials are skipped and logged as warnings.

## Run One Provider

Provider selection is controlled by the `tools` list for the `cloudinventory` module in `configs/local.yml`. The `-aws` option selects AWS profiles; it does not select the AWS provider by itself.

For AWS only:

```yaml
- workflowName: 'cloudinventory'
  workflowConfig:
    - moduleName: cloudinventory
      tools: ['AWSInventory']
      order: 1
      enabled: true
```

```shell
mantis scan -o org_name -w cloudinventory -aws account-prod
```

For Azure only, set:

```yaml
tools: ['AzureInventory']
```

For Cloudflare only, set:

```yaml
tools: ['CloudflareInventory']
```

You can also combine selected providers:

```yaml
tools: ['AWSInventory', 'AzureInventory']
```

## View Cloud Inventory Results

List active cloud assets across all providers:

```shell
mantis list -c
```

Filter by provider:

```shell
mantis list -c -P aws
mantis list -c -P azure
mantis list -c -P cloudflare
```

Show only publicly exposed resources:

```shell
mantis list -c --public-only
mantis list -c -P cloudflare --public-only
```

Include resources that were not found in the latest sync:

```shell
mantis list -c --all
```

Filter by resource type or organization:

```shell
mantis list -c --type StorageAccount -o org_name
```
