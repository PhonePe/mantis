import logging
from mantis.utils.config_utils import ConfigUtils

class ReportWorkflow:

    @staticmethod
    async def executor():

        report = ConfigUtils.get_report_dict()

        logging.info("Generating report yaml block as dictionary")
        print(f"Report: {report}")
