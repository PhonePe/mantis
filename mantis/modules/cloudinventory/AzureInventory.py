import os
import logging
import importlib

from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.config_parsers.config_client import ConfigProvider
from mantis.utils.crud_utils import CrudUtils
from mantis.constants import CLOUD_PROVIDER_AZURE
from mantis.modules.cloudinventory import build_cloud_asset

'''
AzureInventory collects internet-exposable Azure resources using the official
Azure Management SDKs (azure-identity + azure-mgmt-*). Each resource category is
collected by an independent, fault-isolated collector so a missing SDK package
or a permission error on one category never aborts the whole sync.

Credentials resolution order:
  1. cloud.azure.{tenant_id, client_id, client_secret} from local.yml
  2. AZURE_TENANT_ID / AZURE_CLIENT_ID / AZURE_CLIENT_SECRET environment vars

Subscriptions: cloud.azure.subscription_ids (empty = all accessible subscriptions).

Coverage (resource types that can be exposed to the internet):
  - Public IP Addresses (covers VM/LB/App Gateway/Firewall/Bastion/Gateway/NAT
    exposure through association)
  - Load Balancers, Application Gateways, Azure Firewalls, NAT Gateways,
    Bastion Hosts
  - App Services / Function Apps
  - Storage Accounts (blob/file/etc. public endpoints)
  - SQL Servers, PostgreSQL & MySQL servers
  - Cosmos DB accounts
  - AKS managed clusters
  - API Management services
  - Redis caches
  - Container Registries
  - Key Vaults
  - CDN / Front Door endpoints
  - Traffic Manager profiles
  - Cognitive Search services
  - Container Instances
'''


class AzureInventory(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        az_config = ConfigProvider.get_config().cloud.azure
        tenant_id = az_config.tenant_id or os.environ.get("AZURE_TENANT_ID")
        client_id = az_config.client_id or os.environ.get("AZURE_CLIENT_ID")
        client_secret = az_config.client_secret or os.environ.get("AZURE_CLIENT_SECRET")

        if not (tenant_id and client_id and client_secret):
            logging.warning("Azure credentials not provided (cloud.azure.* or AZURE_* env vars)")
            return []

        subscriptions = az_config.subscription_ids or self._enumerate_subscriptions(
            tenant_id, client_id, client_secret
        )
        if not subscriptions:
            logging.warning("No accessible Azure subscriptions found")
            return []

        # One command tuple per subscription (account) → parallelizes across Ray actors.
        tool_tuples = []
        for sub_id in subscriptions:
            inst = AzureInventory()
            inst.args = args
            inst.account = sub_id
            tool_tuples.append((inst, sub_id))
        return tool_tuples

    def _enumerate_subscriptions(self, tenant_id, client_id, client_secret):
        try:
            from azure.identity import ClientSecretCredential
        except ImportError:
            logging.error("azure-identity not installed")
            return []
        try:
            credential = ClientSecretCredential(
                tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
            )
            mod = importlib.import_module("azure.mgmt.resource")
            client = mod.SubscriptionClient(credential)
            return [sub.subscription_id for sub in client.subscriptions.list()]
        except Exception as e:
            logging.warning(f"Unable to list Azure subscriptions: {e}")
            return []

    async def execute(self, tooltuple):
        results = {"success": 0, "failure": 0}
        sub_id = self.account
        logging.info(f"Collecting Azure inventory for subscription: {sub_id}")

        az_config = ConfigProvider.get_config().cloud.azure
        tenant_id = az_config.tenant_id or os.environ.get("AZURE_TENANT_ID")
        client_id = az_config.client_id or os.environ.get("AZURE_CLIENT_ID")
        client_secret = az_config.client_secret or os.environ.get("AZURE_CLIENT_SECRET")

        try:
            from azure.identity import ClientSecretCredential
        except ImportError:
            msg = "azure-identity not installed"
            logging.error(msg)
            results["failure"] = 1
            results["exception"] = msg
            return results

        try:
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
            )

            collectors = [
                self._collect_public_ips,
                self._collect_load_balancers,
                self._collect_application_gateways,
                self._collect_azure_firewalls,
                self._collect_nat_gateways,
                self._collect_bastion_hosts,
                self._collect_app_services,
                self._collect_storage_accounts,
                self._collect_sql_servers,
                self._collect_postgresql,
                self._collect_mysql,
                self._collect_cosmosdb,
                self._collect_aks,
                self._collect_api_management,
                self._collect_redis,
                self._collect_container_registries,
                self._collect_key_vaults,
                self._collect_cdn,
                self._collect_traffic_manager,
                self._collect_search,
                self._collect_container_instances,
            ]

            cloud_assets = []
            for collector in collectors:
                try:
                    collector(sub_id, cloud_assets)
                except Exception as e:
                    logging.debug(f"{collector.__name__} failed for {sub_id}: {e}")

            summary = await CrudUtils.sync_cloud_assets(
                CLOUD_PROVIDER_AZURE, self.args.org, sub_id, cloud_assets
            )
            results["success"] = 1
            results["output"] = (f"Azure[{sub_id}]: {summary['written']} synced, "
                                 f"{summary['created']} new, {summary['removed']} removed, "
                                 f"{summary['deactivated']} inactive")
            logging.info(results["output"])
        except Exception as e:
            logging.error(f"Azure inventory error ({sub_id}): {e}")
            results["failure"] = 1
            results["exception"] = str(e)

        return results

    # ---- helpers -----------------------------------------------------------

    def _client(self, import_path, class_name, sub_id):
        """Lazily build an azure-mgmt client; returns None if the package is missing."""
        try:
            mod = importlib.import_module(import_path)
            client_cls = getattr(mod, class_name)
            return client_cls(self.credential, sub_id)
        except ImportError:
            logging.warning(f"{import_path} not installed; skipping that resource type")
            return None

    def _add(self, cloud_assets, sub_id, resource_id, resource_type, name, location,
             is_public, ips=None, fqdns=None, properties=None):
        if not resource_id:
            return
        cloud_assets.append(build_cloud_asset(
            provider=CLOUD_PROVIDER_AZURE,
            resource_id=resource_id,
            resource_type=resource_type,
            org=self.args.org,
            name=name,
            account_id=sub_id,
            region=location,
            is_public=is_public,
            public_ips=ips or [],
            public_fqdns=fqdns or [],
            properties=properties or {},
        ))

    @staticmethod
    def _enabled(value):
        # Azure exposes public network access as 'Enabled'/'Disabled' (case varies).
        return str(value).lower() != "disabled" if value is not None else True

    # ---- network primitives ------------------------------------------------

    def _collect_public_ips(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.network", "NetworkManagementClient", sub_id)
        if client is None:
            return
        for pip in client.public_ip_addresses.list_all():
            ip = pip.ip_address
            fqdn = pip.dns_settings.fqdn if pip.dns_settings else None
            associated = pip.ip_configuration.id if pip.ip_configuration else None
            self._add(
                cloud_assets, sub_id, pip.id, "PublicIPAddress", pip.name, pip.location,
                is_public=bool(ip),
                ips=[ip] if ip else [],
                fqdns=[fqdn] if fqdn else [],
                properties={"allocation": pip.public_ip_allocation_method, "associated_to": associated},
            )

    def _collect_load_balancers(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.network", "NetworkManagementClient", sub_id)
        if client is None:
            return
        for lb in client.load_balancers.list_all():
            public = any(getattr(f, "public_ip_address", None) for f in (lb.frontend_ip_configurations or []))
            self._add(
                cloud_assets, sub_id, lb.id, "LoadBalancer", lb.name, lb.location,
                is_public=public,
                properties={"sku": lb.sku.name if lb.sku else None},
            )

    def _collect_application_gateways(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.network", "NetworkManagementClient", sub_id)
        if client is None:
            return
        for gw in client.application_gateways.list_all():
            public = any(getattr(f, "public_ip_address", None) for f in (gw.frontend_ip_configurations or []))
            self._add(
                cloud_assets, sub_id, gw.id, "ApplicationGateway", gw.name, gw.location,
                is_public=public,
                properties={"tier": gw.sku.tier if gw.sku else None},
            )

    def _collect_azure_firewalls(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.network", "NetworkManagementClient", sub_id)
        if client is None:
            return
        for fw in client.azure_firewalls.list_all():
            ips = [c.public_ip_address.id for c in (fw.ip_configurations or []) if getattr(c, "public_ip_address", None)]
            self._add(
                cloud_assets, sub_id, fw.id, "AzureFirewall", fw.name, fw.location,
                is_public=bool(ips),
                properties={"public_ip_count": len(ips)},
            )

    def _collect_nat_gateways(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.network", "NetworkManagementClient", sub_id)
        if client is None:
            return
        for nat in client.nat_gateways.list_all():
            public = bool(nat.public_ip_addresses)
            self._add(
                cloud_assets, sub_id, nat.id, "NatGateway", nat.name, nat.location,
                is_public=public,
            )

    def _collect_bastion_hosts(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.network", "NetworkManagementClient", sub_id)
        if client is None:
            return
        for host in client.bastion_hosts.list():
            self._add(
                cloud_assets, sub_id, host.id, "BastionHost", host.name, host.location,
                is_public=True,
            )

    # ---- PaaS endpoints ----------------------------------------------------

    def _collect_app_services(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.web", "WebSiteManagementClient", sub_id)
        if client is None:
            return
        for app in client.web_apps.list():
            hostnames = list(app.enabled_host_names or app.host_names or [])
            public = self._enabled(getattr(app, "public_network_access", None)) and bool(hostnames)
            rt = "FunctionApp" if app.kind and "functionapp" in app.kind else "AppService"
            self._add(
                cloud_assets, sub_id, app.id, rt, app.name, app.location,
                is_public=public, fqdns=hostnames,
                properties={"state": app.state, "kind": app.kind},
            )

    def _collect_storage_accounts(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.storage", "StorageManagementClient", sub_id)
        if client is None:
            return
        for acct in client.storage_accounts.list():
            default_action = None
            if acct.network_rule_set and acct.network_rule_set.default_action:
                default_action = str(acct.network_rule_set.default_action)
            public = (
                self._enabled(getattr(acct, "public_network_access", None))
                and (bool(getattr(acct, "allow_blob_public_access", False))
                     or (default_action or "Allow").lower() == "allow")
            )
            endpoints = []
            if acct.primary_endpoints:
                endpoints = [v for v in vars(acct.primary_endpoints).values() if isinstance(v, str) and v]
            self._add(
                cloud_assets, sub_id, acct.id, "StorageAccount", acct.name, acct.location,
                is_public=public, fqdns=endpoints,
                properties={"default_action": default_action,
                            "allow_blob_public_access": getattr(acct, "allow_blob_public_access", None)},
            )

    def _collect_sql_servers(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.sql", "SqlManagementClient", sub_id)
        if client is None:
            return
        for srv in client.servers.list():
            fqdn = srv.fully_qualified_domain_name
            public = self._enabled(getattr(srv, "public_network_access", None))
            self._add(
                cloud_assets, sub_id, srv.id, "SqlServer", srv.name, srv.location,
                is_public=public, fqdns=[fqdn] if fqdn else [],
                properties={"version": srv.version},
            )

    def _collect_postgresql(self, sub_id, cloud_assets):
        for path, cls, rt in (
            ("azure.mgmt.rdbms.postgresql", "PostgreSQLManagementClient", "PostgreSQLServer"),
            ("azure.mgmt.rdbms.postgresql_flexibleservers", "PostgreSQLManagementClient", "PostgreSQLFlexibleServer"),
        ):
            client = self._client(path, cls, sub_id)
            if client is None:
                continue
            try:
                for srv in client.servers.list():
                    fqdn = getattr(srv, "fully_qualified_domain_name", None)
                    public = self._enabled(getattr(srv, "public_network_access", None))
                    self._add(cloud_assets, sub_id, srv.id, rt, srv.name, srv.location,
                              is_public=public, fqdns=[fqdn] if fqdn else [])
            except Exception as e:
                logging.debug(f"{rt} listing failed for {sub_id}: {e}")

    def _collect_mysql(self, sub_id, cloud_assets):
        for path, cls, rt in (
            ("azure.mgmt.rdbms.mysql", "MySQLManagementClient", "MySQLServer"),
            ("azure.mgmt.rdbms.mysql_flexibleservers", "MySQLManagementClient", "MySQLFlexibleServer"),
        ):
            client = self._client(path, cls, sub_id)
            if client is None:
                continue
            try:
                for srv in client.servers.list():
                    fqdn = getattr(srv, "fully_qualified_domain_name", None)
                    public = self._enabled(getattr(srv, "public_network_access", None))
                    self._add(cloud_assets, sub_id, srv.id, rt, srv.name, srv.location,
                              is_public=public, fqdns=[fqdn] if fqdn else [])
            except Exception as e:
                logging.debug(f"{rt} listing failed for {sub_id}: {e}")

    def _collect_cosmosdb(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.cosmosdb", "CosmosDBManagementClient", sub_id)
        if client is None:
            return
        for acct in client.database_accounts.list():
            endpoint = acct.document_endpoint
            public = self._enabled(getattr(acct, "public_network_access", None))
            self._add(
                cloud_assets, sub_id, acct.id, "CosmosDBAccount", acct.name, acct.location,
                is_public=public, fqdns=[endpoint] if endpoint else [],
                properties={"kind": acct.kind},
            )

    def _collect_aks(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.containerservice", "ContainerServiceClient", sub_id)
        if client is None:
            return
        for cluster in client.managed_clusters.list():
            fqdn = cluster.fqdn
            private = False
            if cluster.api_server_access_profile:
                private = bool(cluster.api_server_access_profile.enable_private_cluster)
            self._add(
                cloud_assets, sub_id, cluster.id, "AKSCluster", cluster.name, cluster.location,
                is_public=(not private) and bool(fqdn), fqdns=[fqdn] if fqdn else [],
                properties={"kubernetes_version": cluster.kubernetes_version, "private_cluster": private},
            )

    def _collect_api_management(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.apimanagement", "ApiManagementClient", sub_id)
        if client is None:
            return
        for svc in client.api_management_service.list():
            fqdns = [svc.gateway_url] if svc.gateway_url else []
            public = self._enabled(getattr(svc, "public_network_access", None))
            self._add(
                cloud_assets, sub_id, svc.id, "ApiManagement", svc.name, svc.location,
                is_public=public, ips=list(svc.public_ip_addresses or []), fqdns=fqdns,
            )

    def _collect_redis(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.redis", "RedisManagementClient", sub_id)
        if client is None:
            return
        for cache in client.redis.list_by_subscription():
            host = cache.host_name
            public = self._enabled(getattr(cache, "public_network_access", None))
            self._add(
                cloud_assets, sub_id, cache.id, "RedisCache", cache.name, cache.location,
                is_public=public, fqdns=[host] if host else [],
            )

    def _collect_container_registries(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.containerregistry", "ContainerRegistryManagementClient", sub_id)
        if client is None:
            return
        for reg in client.registries.list():
            login = reg.login_server
            public = self._enabled(getattr(reg, "public_network_access", None))
            self._add(
                cloud_assets, sub_id, reg.id, "ContainerRegistry", reg.name, reg.location,
                is_public=public, fqdns=[login] if login else [],
            )

    def _collect_key_vaults(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.keyvault", "KeyVaultManagementClient", sub_id)
        if client is None:
            return
        for vault in client.vaults.list_by_subscription():
            props = getattr(vault, "properties", None)
            uri = getattr(props, "vault_uri", None) if props else None
            public = self._enabled(getattr(props, "public_network_access", None)) if props else True
            self._add(
                cloud_assets, sub_id, vault.id, "KeyVault", vault.name, getattr(vault, "location", None),
                is_public=public, fqdns=[uri] if uri else [],
            )

    def _collect_cdn(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.cdn", "CdnManagementClient", sub_id)
        if client is None:
            return
        for profile in client.profiles.list():
            rg = profile.id.split("/resourceGroups/")[1].split("/")[0]
            for endpoint in client.endpoints.list_by_profile(rg, profile.name):
                host = endpoint.host_name
                self._add(
                    cloud_assets, sub_id, endpoint.id, "CDNEndpoint", endpoint.name, endpoint.location,
                    is_public=True, fqdns=[host] if host else [],
                    properties={"profile": profile.name},
                )

    def _collect_traffic_manager(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.trafficmanager", "TrafficManagerManagementClient", sub_id)
        if client is None:
            return
        for profile in client.profiles.list_by_subscription():
            fqdn = profile.dns_config.fqdn if profile.dns_config else None
            self._add(
                cloud_assets, sub_id, profile.id, "TrafficManagerProfile", profile.name, "global",
                is_public=True, fqdns=[fqdn] if fqdn else [],
            )

    def _collect_search(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.search", "SearchManagementClient", sub_id)
        if client is None:
            return
        for svc in client.services.list_by_subscription():
            public = self._enabled(getattr(svc, "public_network_access", None))
            host = f"{svc.name}.search.windows.net"
            self._add(
                cloud_assets, sub_id, svc.id, "SearchService", svc.name, svc.location,
                is_public=public, fqdns=[host],
            )

    def _collect_container_instances(self, sub_id, cloud_assets):
        client = self._client("azure.mgmt.containerinstance", "ContainerInstanceManagementClient", sub_id)
        if client is None:
            return
        for group in client.container_groups.list():
            ip_obj = group.ip_address
            is_public = bool(ip_obj and str(getattr(ip_obj, "type", "")).lower() == "public")
            ip = ip_obj.ip if ip_obj else None
            fqdn = ip_obj.fqdn if ip_obj else None
            self._add(
                cloud_assets, sub_id, group.id, "ContainerGroup", group.name, group.location,
                is_public=is_public,
                ips=[ip] if ip and is_public else [],
                fqdns=[fqdn] if fqdn else [],
            )
