import logging
from mantis.models.args_model import ArgsModel
from mantis.utils.list_subcommand_utils import get_orgs, get_domains


class ListWorkflow:

    @staticmethod
    async def executor(args: ArgsModel):
        
        if args.list_orgs:
            logging.info("Getting orgs from database")
            orgs = await get_orgs()
            if orgs:
                print(f"\nTotal Number of orgs onboarded: {len(orgs)}\n")
                print("\n".join(orgs))
            else:
                logging.info("No orgs found in database")

        if args.list_domains:
            logging.info("Getting subdomains from database")
            domains = await get_domains(args.orgs_list, args.asset_types_list, args.after_datetime_filter, args.before_datetime_filter)
            if domains:
                print(f"\nOrgs Filter: {','.join(args.orgs_list)}")
                print(f"Total Domains Found based on provided filters: {len(domains)}\n")
                print('\n'.join(domains))
            else:
                logging.info("No domains found")
