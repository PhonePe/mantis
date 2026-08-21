import logging
from mantis.models.args_model import ArgsModel
from mantis.utils.list_subcommand_utils import get_orgs, get_domains, get_cloud_assets


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

        if args.list_cloud:
            logging.info("Getting cloud resources from database")
            orgs = args.orgs_list if args.orgs_list else None
            resources = await get_cloud_assets(
                orgs=orgs,
                provider=args.cloud_provider_filter,
                resource_type=args.cloud_type_filter,
                public_only=args.cloud_public_only,
                include_inactive=args.cloud_include_inactive,
            )
            if resources:
                print(f"\n{'PROVIDER':<12}{'TYPE':<26}{'NAME':<34}{'PUBLIC':<8}{'ACTIVE':<8}{'REGION':<16}")
                print("-" * 104)
                for r in resources:
                    print(
                        f"{str(r.get('provider', '')):<12}"
                        f"{str(r.get('resource_type', ''))[:24]:<26}"
                        f"{str(r.get('name', ''))[:32]:<34}"
                        f"{str(r.get('is_public', False)):<8}"
                        f"{str(r.get('is_active', True)):<8}"
                        f"{str(r.get('region', '')):<16}"
                    )
                print(f"\nTotal cloud resources found based on provided filters: {len(resources)}\n")
            else:
                logging.info("No cloud resources found")
