import logging
from mantis.config_parsers.config_client import ConfigProvider

class ReportWorkflow:

    @staticmethod
    async def executor():
        report = ConfigProvider.get_config().report
        print(f"Report: {report}")
