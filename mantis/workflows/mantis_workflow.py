from mantis.models.args_model import ArgsModel
from mantis.modules.workflow import Workflow
from mantis.workflows.list_workflow import ListWorkflow
from mantis.workflows.report_workflow import ReportWorkflow
import asyncio

class MantisWorkflow:
    @staticmethod
    def select_workflow(args: ArgsModel) -> None:

        if args.list_:
            asyncio.run(ListWorkflow.executor(args))
        elif args.report_:
            asyncio.run(ReportWorkflow.executor())
        else:
            asyncio.run(Workflow.workflow_executor(args))
        
