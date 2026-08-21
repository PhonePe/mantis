import logging
from mantis.config_parsers.config_client import ConfigProvider
from mantis.config_parsers.config_models import Module

class ConfigUtils:

    @staticmethod
    def get_module_dict(workflowName):
        workflows = ConfigProvider.get_config().workflow
        for workflow in workflows:
            if workflow.workflowName == workflowName:
                return workflow

    
    @staticmethod
    def get_ordered_module_list(workflow):
        workflow_dict = [Module.parse_obj(module).dict() for module in workflow.workflowConfig]
        ordered_workflow = sorted(workflow_dict, key=lambda x : x['order'])
        return [module['moduleName'] for module in ordered_workflow]


    @staticmethod
    def filter_modules(ordered_modules, workflow, args):
        """Filter ordered modules by the module 'enabled' flag and CLI --modules/--skip-modules overrides."""
        selected = getattr(args, 'modules', None)
        skipped = getattr(args, 'skip_modules', None)

        filtered = []
        for module_name in ordered_modules:
            module = ConfigUtils.get_module(module_name=module_name, workflow=workflow)

            if selected:
                if module_name not in selected:
                    continue
            elif module is not None and not getattr(module, 'enabled', True):
                # a disabled module runs only when explicitly requested via --modules
                logging.debug(f"Skipping disabled module: {module_name}")
                continue

            if skipped and module_name in skipped:
                logging.debug(f"Skipping module via --skip-modules: {module_name}")
                continue

            filtered.append(module_name)

        return filtered


    @staticmethod
    def get_module(module_name, workflow):
        for module in workflow.workflowConfig:
            if module.moduleName == module_name: 
                return module
            
    @staticmethod
    def is_scanNewOnly_tool(tool_name, args):
        workflow = ConfigUtils.get_module_dict(args.workflow)
        if workflow.scanNewOnly:
            ## Check tool in module
            module = ConfigUtils.get_module("discovery", workflow)
            if tool_name in module.tools:
                return False
            else:
                return True
