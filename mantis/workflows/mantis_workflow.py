from mantis.models.args_model import ArgsModel
from mantis.modules.workflow import Workflow
from mantis.workflows.list_workflow import ListWorkflow
import asyncio

class MantisWorkflow:
    @staticmethod
    def select_workflow(args: ArgsModel) -> None:

        if args.list_:
            asyncio.run(ListWorkflow.executor(args))
        else:
            asyncio.run(Workflow.workflow_executor(args))
        