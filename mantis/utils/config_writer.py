import os
import logging
import yaml

from mantis.constants import CLOUD_INVENTORY_MODULE, CLOUD_PROVIDER_TOOL_MAP

CONFIG_PATH = os.path.join('configs', 'local.yml')


class ConfigWriter:
    """Persist enable/disable changes for cloud inventory providers to local.yml.

    Toggling a provider adds or removes its inventory tool (e.g. AzureInventory)
    from the cloudinventory module across every workflow that defines it.
    """

    @staticmethod
    def _load():
        with open(CONFIG_PATH, 'r') as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    @staticmethod
    def _dump(config):
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    @staticmethod
    def set_cloud_provider_enabled(provider: str, enabled: bool) -> bool:
        tool_name = CLOUD_PROVIDER_TOOL_MAP.get(provider)
        if not tool_name:
            logging.error(f"Unknown cloud provider: {provider}")
            return False

        try:
            config = ConfigWriter._load()
        except OSError as e:
            logging.error(f"Unable to read config {CONFIG_PATH}: {e}")
            return False

        changed = False
        for workflow in config.get('workflow', []):
            for module in workflow.get('workflowConfig', []):
                if module.get('moduleName') != CLOUD_INVENTORY_MODULE:
                    continue
                tools = module.setdefault('tools', [])
                if enabled and tool_name not in tools:
                    tools.append(tool_name)
                    changed = True
                elif not enabled and tool_name in tools:
                    tools.remove(tool_name)
                    changed = True

                # Keep the module 'enabled' flag consistent with its tools so
                # the change takes effect in regular scans immediately.
                if enabled and not module.get('enabled', True):
                    module['enabled'] = True
                    changed = True
                elif not enabled and not tools and module.get('enabled', True):
                    module['enabled'] = False
                    changed = True

        if not changed:
            logging.info(
                f"No cloudinventory module found or {tool_name} already "
                f"{'enabled' if enabled else 'disabled'}. No changes written."
            )
            return False

        ConfigWriter._dump(config)
        logging.info(
            f"{'Enabled' if enabled else 'Disabled'} cloud provider "
            f"'{provider}' ({tool_name}) in {CONFIG_PATH}"
        )
        return True
