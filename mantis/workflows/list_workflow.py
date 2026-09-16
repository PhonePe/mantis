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
                header = (f"{'PROVIDER':<11}{'TYPE':<22}{'NAME':<28}{'PUBLIC':<7}"
                          f"{'ACTIVE':<7}{'REGION':<14}{'ACCOUNT':<26}ENDPOINTS (IPs / FQDNs)")
                print(f"\n{header}")
                print("-" * len(header))
                for r in resources:
                    endpoints = ", ".join((r.get('public_ips') or []) + (r.get('public_fqdns') or [])) or "-"
                    print(
                        f"{str(r.get('provider', '')):<11}"
                        f"{str(r.get('resource_type', ''))[:20]:<22}"
                        f"{str(r.get('name', ''))[:26]:<28}"
                        f"{str(r.get('is_public', False)):<7}"
                        f"{str(r.get('is_active', True)):<7}"
                        f"{str(r.get('region', '')):<14}"
                        f"{str(r.get('account_id', ''))[:24]:<26}"
                        f"{endpoints}"
                    )
                print(f"\nTotal cloud resources found based on provided filters: {len(resources)}\n")
            else:
                logging.info("No cloud resources found")
