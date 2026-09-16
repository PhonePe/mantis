import logging

from mantis.models.args_model import ArgsModel
from mantis.utils.crud_utils import CrudUtils
from mantis.db.crud_cloud_assets import read_cloud_assets
from mantis.utils.config_writer import ConfigWriter
from mantis.constants import CLOUD_PROVIDER_TOOL_MAP
from mantis.modules.cloudinventory.CloudflareInventory import CloudflareInventory
from mantis.modules.cloudinventory.AzureInventory import AzureInventory
from mantis.modules.cloudinventory.AWSInventory import AWSInventory

PROVIDER_CLASS_MAP = {
    "cloudflare": CloudflareInventory,
    "azure": AzureInventory,
    "aws": AWSInventory,
}


class CloudWorkflow:

    @staticmethod
    async def executor(args: ArgsModel) -> None:
        action = args.cloud_action

        if action == "sync":
            await CloudWorkflow._sync(args)
        elif action == "list":
            await CloudWorkflow._list(args)
        elif action in ("enable", "disable"):
            CloudWorkflow._toggle(args, enabled=(action == "enable"))
        else:
            logging.error(f"Unknown cloud action: {action}")

    @staticmethod
    async def _sync(args: ArgsModel) -> None:
        providers = [args.cloud_provider] if args.cloud_provider else list(PROVIDER_CLASS_MAP.keys())

        for provider in providers:
            tool_class = PROVIDER_CLASS_MAP.get(provider)
            if tool_class is None:
                logging.warning(f"Unknown provider: {provider}")
                continue

            tool = tool_class()
            tool_tuple = await tool.init(args)
            for single_tool in tool_tuple:
                result = await single_tool[0].execute(single_tool)
                logging.info(f"{provider} sync result: {result}")

    @staticmethod
    async def _list(args: ArgsModel) -> None:
        query = {"org": args.org}
        if args.cloud_provider:
            query["provider"] = args.cloud_provider
        if args.cloud_type:
            query["resource_type"] = args.cloud_type
        if args.cloud_public_only:
            query["is_public"] = True

        resources = await read_cloud_assets(query)
        if not resources:
            print("No cloud resources found for the given filters.")
            return

        print(f"\n{'PROVIDER':<12}{'TYPE':<24}{'NAME':<32}{'PUBLIC':<8}{'REGION':<16}")
        print("-" * 92)
        for r in resources:
            print(
                f"{r.get('provider', ''):<12}"
                f"{str(r.get('resource_type', '')):<24}"
                f"{str(r.get('name', ''))[:30]:<32}"
                f"{str(r.get('is_public', False)):<8}"
                f"{str(r.get('region', '')):<16}"
            )
        print(f"\nTotal: {len(resources)} resource(s)\n")

    @staticmethod
    def _toggle(args: ArgsModel, enabled: bool) -> None:
        provider = args.cloud_provider
        if provider not in CLOUD_PROVIDER_TOOL_MAP:
            logging.error(f"Unknown provider: {provider}")
            return
        ConfigWriter.set_cloud_provider_enabled(provider, enabled)
