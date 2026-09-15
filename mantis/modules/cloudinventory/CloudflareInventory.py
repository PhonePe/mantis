import os
import logging

from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.config_parsers.config_client import ConfigProvider
from mantis.utils.crud_utils import CrudUtils
from mantis.constants import CLOUD_PROVIDER_CLOUDFLARE
from mantis.modules.cloudinventory import build_cloud_asset

'''
CloudflareInventory enumerates Cloudflare zones and their DNS records and stores
them as cloud resources in the cloud_assets_collection. Each zone is emitted as
its own command tuple so zones parallelize across Ray actors.

Credentials resolution order:
    1. cloud.cloudflare.api_token from local.yml
    2. CF_API_TOKEN environment variable
    3. cloud.cloudflare.email / api_key from local.yml
    4. CF_API_EMAIL / CF_API_KEY environment variables

A DNS record that is not proxied through Cloudflare is treated as publicly
exposed (its origin is directly reachable).
'''


class CloudflareInventory(BaseScanner):

    @staticmethod
    def _credentials():
        cf_config = ConfigProvider.get_config().cloud.cloudflare
        token = cf_config.api_token or os.environ.get("CF_API_TOKEN")
        if token:
            return {"email": "", "key": token}

        email = cf_config.email or os.environ.get("CF_API_EMAIL")
        api_key = cf_config.api_key or os.environ.get("CF_API_KEY")
        if email and api_key:
            return {"email": email, "key": api_key}
        return None

    async def init(self, args: ArgsModel):
        self.args = args
        credentials = self._credentials()

        if not credentials:
            logging.warning("Cloudflare credentials not provided (API token or email/API key)")
            return []

        try:
            import CloudFlare
        except ImportError:
            logging.error("cloudflare package not installed")
            return []

        zones = self._enumerate_zones(credentials)

        # One command tuple per zone (account) → parallelizes across Ray actors.
        tool_tuples = []
        for zone in zones:
            inst = CloudflareInventory()
            inst.args = args
            inst.account = zone
            tool_tuples.append((inst, zone['name']))
        return tool_tuples

    def _enumerate_zones(self, credentials):
        import CloudFlare
        per_page = 100
        zones = []
        try:
            cf = CloudFlare.CloudFlare(credentials["email"], credentials["key"], raw=True)
            first_page = cf.zones.get(params={'per_page': per_page, 'page': 1})
            total_pages = first_page['result_info']['total_pages']
            for zone_page in range(1, total_pages + 1):
                page = cf.zones.get(params={'per_page': per_page, 'page': zone_page})
                for zone in page['result']:
                    zones.append({
                        'id': zone['id'],
                        'name': zone['name'],
                        'status': zone.get('status'),
                        'paused': zone.get('paused'),
                    })
        except Exception as e:
            logging.error(f"Cloudflare zone enumeration error: {e}")
        return zones

    async def execute(self, tooltuple):
        results = {"success": 0, "failure": 0}
        zone = self.account
        zone_id = zone['id']
        logging.info(f"Collecting Cloudflare inventory for zone: {zone['name']}")

        credentials = self._credentials()

        try:
            import CloudFlare
        except ImportError:
            msg = "cloudflare package not installed"
            logging.error(msg)
            results["failure"] = 1
            results["exception"] = msg
            return results

        cloud_assets = []
        try:
            cf = CloudFlare.CloudFlare(credentials["email"], credentials["key"], raw=True)
            self._collect_zone(cf, zone, cloud_assets)

            summary = await CrudUtils.sync_cloud_assets(
                CLOUD_PROVIDER_CLOUDFLARE, self.args.org, zone_id, cloud_assets
            )
            results["success"] = 1
            results["output"] = (f"Cloudflare[{zone['name']}]: {summary['written']} synced, "
                                 f"{summary['created']} new, {summary['removed']} removed, "
                                 f"{summary['deactivated']} inactive")
            logging.info(results["output"])
        except Exception as e:
            logging.error(f"Cloudflare inventory error ({zone['name']}): {e}")
            results["failure"] = 1
            results["exception"] = str(e)

        return results

    def _collect_zone(self, cf, zone, cloud_assets):
        per_page = 100
        zone_id = zone['id']
        zone_name = zone['name']

        cloud_assets.append(build_cloud_asset(
            provider=CLOUD_PROVIDER_CLOUDFLARE,
            resource_id=zone_id,
            resource_type="DNSZone",
            org=self.args.org,
            name=zone_name,
            account_id=zone_id,
            region="global",
            is_public=True,
            public_fqdns=[zone_name],
            properties={"status": zone.get('status'), "paused": zone.get('paused')},
        ))

        records_first = cf.zones.dns_records.get(zone_id, params={'per_page': per_page, 'page': 1})
        record_pages = records_first['result_info']['total_pages']

        for record_page in range(1, record_pages + 1):
            records = cf.zones.dns_records.get(
                zone_id, params={'per_page': per_page, 'page': record_page}
            )['result']
            for record in records:
                proxied = record.get('proxied', False)
                cloud_assets.append(build_cloud_asset(
                    provider=CLOUD_PROVIDER_CLOUDFLARE,
                    resource_id=f"{zone_id}:{record['id']}",
                    resource_type=f"DNSRecord/{record.get('type')}",
                    org=self.args.org,
                    name=record.get('name'),
                    account_id=zone_id,
                    region="global",
                    is_public=not proxied,
                    public_fqdns=[record.get('name')],
                    properties={
                        "type": record.get('type'),
                        "content": record.get('content'),
                        "proxied": proxied,
                    },
                ))
