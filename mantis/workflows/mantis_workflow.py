from mantis.models.args_model import ArgsModel
from mantis.modules.workflow import Workflow
from mantis.workflows.list_workflow import ListWorkflow
from mantis.workflows.report_workflow import ReportWorkflow
from mantis.workflows.deboard_workflow import DeboardWorkflow
import asyncio

class MantisWorkflow:
    @staticmethod
    def select_workflow(args: ArgsModel) -> None:

        if args.list_:
            asyncio.run(ListWorkflow.executor(args))
        elif args.report_:
            asyncio.run(ReportWorkflow.executor())
        elif args.deboard_:
            asyncio.run(DeboardWorkflow.executor(args))
        else:
            asyncio.run(Workflow.workflow_executor(args))
        
