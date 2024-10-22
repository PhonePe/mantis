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

    @staticmethod
    def get_report_dict():
        report = ConfigProvider.get_config().report
        return report
