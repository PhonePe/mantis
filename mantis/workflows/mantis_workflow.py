from mantis.models.args_model import ArgsModel
from mantis.modules.workflow import Workflow
import asyncio

class MantisWorkflow:
    @staticmethod
    def select_workflow(args: ArgsModel) -> None:

        asyncio.run(Workflow.workflow_executor(args))
        