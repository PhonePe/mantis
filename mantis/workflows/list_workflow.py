import logging
from mantis.models.args_model import ArgsModel
from mantis.utils.list_subcommand_utils import get_orgs

class ListWorkflow:

    @staticmethod
    async def executor(args: ArgsModel):

        if args.list_orgs:
            logging.info("Getting orgs from database")
            orgs = await get_orgs()
            print()
            print(f'''Total Number of orgs onboarded: {len(orgs)}''')
            print()
            for org in orgs:
                print(org)