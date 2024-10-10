import logging
import argparse
from sys import argv
from argparse import ArgumentParser

from mantis.models.args_model import ArgsModel

class CustomFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, width=200, max_help_position=70 )
    

class ArgsParse:
    @staticmethod
    def msg(name=None):                                                            
        return '''
        \033[1;34mONBOARD: (First time scan, Run this !!)\033[0m

        \033[0;32mmantis onboard -o example_org -t www.example.org\033[0m
        \033[0;32mmantis onboard -o example_org -f file.txt\033[0m

        \033[1;34mSCAN:\033[0m

        \033[0;32mmantis scan -o example_org\033[0m
        \033[0;32mmantis scan -o example_org -a example_app\033[0m
            '''
    
    @staticmethod
    def onboard_msg(name=None):                                                            
        return '''
        \033[1;34mONBOARD: (First time scan, Run this !!)\033[0m

        \033[0;32mmantis onboard -o example_org -t example.tld\033[0m
        \033[0;32mmantis onboard -o example_org -f file.txt\033[0m

            '''

    @staticmethod
    def scan_msg(name=None):                                                            
        return '''
        \033[1;34mSCAN:\033[0m

        \033[0;32mmantis scan -o example_org\033[0m
        \033[0;32mmantis scan -o example_org -a example_app\033[0m
            '''
    
    @staticmethod
    def list_msg(name=None):                                                            
        return '''
        \033[1;34mList:\033[0m

        \033[0;32mmantis list {subcommand}\033[0m
            '''
    
    @staticmethod
    def args_parse() -> ArgsModel:
        parsed_args = {}

        parser = ArgumentParser(
                                prog='mantis',
                                formatter_class=CustomFormatter,
                                add_help=False,
                                usage=ArgsParse.msg()
                              )
        
        subparser = parser.add_subparsers(title="TYPE", dest="subcommand")
        
        onboard_parser = subparser.add_parser("onboard", help="Onboard a target", usage=ArgsParse.onboard_msg())

        # parser.add_argument('-m','--mode', choices=['onboard', 'scan'], required=True,
        #            help='Select mode of operation')
        
        onboard_scan_group = onboard_parser.add_mutually_exclusive_group()
            
        parser.add_argument('-h', '--help',
                            dest = 'help',
                            default = "default",
                            help = "list command line options",
                            action = "help")
        
        onboard_scan_group.add_argument('-t', '--host',
                            dest = 'host',
                            help = "top level domain to scan" )
        
        onboard_scan_group.add_argument('-f', '--file_input',
                            dest = 'file_name',
                            help = "path to file containing any combination of TLD, subdomain, IP-range, IP-CIDR")
        
        onboard_parser.add_argument('-w', '--workflow',
                            dest = 'workflow',
                            default = "default",
                            help = "workflow to be executed as specified in config file")
        
        onboard_parser.add_argument('-o', '--org',
                            dest = 'org',
                            required = True,
                            help = "name of the organisation")
        
        onboard_parser.add_argument('-a', '--app',
                            dest = 'app',
                            help = "scan only subdomains that belong to an app",
                            )
        
        onboard_parser.add_argument('-p', '--passive',
                            dest = 'passive',
                            help = 'run passive port scan',
                            action = 'store_true'
                            )
        
        onboard_parser.add_argument('-s', '--stale',
                            dest = 'stale',
                            help = 'mark domains as stale (domains purchased but not in use)',
                            action = 'store_true'
                            )
        
        onboard_parser.add_argument('-i', '--ignore_stale', 
                            dest = 'ignore_stale',
                            help = 'ignore stale domains during scan',
                            action = 'store_true' 
                            )
        
        onboard_parser.add_argument('-tc', '--thread_count', 
                            dest = 'thread_count',
                            help = 'thread count, default 3',
                            )
        
        onboard_parser.add_argument('-r', '--use_ray', 
                            dest = 'use_ray',
                            help = 'use ray framework for distributed scans',
                            action = 'store_true' 
                            )
        
        onboard_parser.add_argument('-n', '--num_actors', 
                            dest = 'num_actors',
                            help = 'number of ray actors, default 3',
                            )
              
        onboard_parser.add_argument('-d', '--delete_logs', 
                            dest = 'delete_logs',
                            help = 'delete logs of previous scans',
                            action = 'store_true'
                            )
        
        onboard_parser.add_argument('-v', '--verbose', 
                            dest = 'verbose',
                            help = 'print debug logs',
                            action = 'store_true'
                            )
        
        onboard_parser.add_argument('-aws', '--aws_profiles', 
                            dest = 'aws_profiles',
                            help = 'List of comma separated aws profiles for Route53',
                            )
        
        onboard_parser.add_argument('--sub', 
                                 dest = 'subdomain',
                                 help='Subdomain to onboard and scan',
                                 action = 'store_true')
        
        
        scan_parser = subparser.add_parser("scan", help="Scan an org", usage=ArgsParse.scan_msg())

        scan_parser.add_argument('-w', '--workflow',
                            dest = 'workflow',
                            default = "default",
                            help = "workflow to be executed as specified in config file")
        
        scan_parser.add_argument('-o', '--org',
                            dest = 'org',
                            required = True,
                            help = "name of the organisation")
        
        scan_parser.add_argument('-a', '--app',
                            dest = 'app',
                            help = "scan only subdomains that belong to an app",
                            )
        
        scan_parser.add_argument('-p', '--passive',
                            dest = 'passive',
                            help = 'run passive port scan',
                            action = 'store_true'
                            )
        
        scan_parser.add_argument('-s', '--stale',
                            dest = 'stale',
                            help = 'mark domains as stale (domains purchased but not in use)',
                            action = 'store_true'
                            )
        
        scan_parser.add_argument('-i', '--ignore_stale', 
                            dest = 'ignore_stale',
                            help = 'ignore stale domains during scan',
                            action = 'store_true' 
                            )
        
        scan_parser.add_argument('-tc', '--thread_count', 
                            dest = 'thread_count',
                            help = 'thread count, default 3',
                            )
        
        scan_parser.add_argument('-r', '--use_ray', 
                            dest = 'use_ray',
                            help = 'use ray framework for distributed scans',
                            action = 'store_true' 
                            )
        
        scan_parser.add_argument('-n', '--num_actors', 
                            dest = 'num_actors',
                            help = 'number of ray actors, default 3',
                            )
        
        scan_parser.add_argument('-d', '--delete_logs', 
                            dest = 'delete_logs',
                            help = 'delete logs of previous scans',
                            action = 'store_true'
                            )
        
        scan_parser.add_argument('-v', '--verbose', 
                            dest = 'verbose',
                            help = 'print debug logs',
                            action = 'store_true'
                            )
        
        scan_parser.add_argument('-aws', '--aws_profiles', 
                            dest = 'aws_profiles',
                            help = 'List of comma separated aws profiles for Route53',
                            )
        
        scan_parser.add_argument('--sub', 
                                 dest = 'subdomain',
                                 help='Subdomain to scan')
        
        
        list_parser = subparser.add_parser("list", help="List entities present in db", usage=ArgsParse.list_msg())
        
        list_parser.add_argument("-l","--list-orgs", help="list all orgs from database", dest="list_sub_command_ls_orgs", action="store_true")
        
        list_parser.add_argument("-d","--list-domains", help="list domains (tlds/subdomains) for selected orgs", dest="list_sub_command_ls_domains", action="store_true")
        list_parser.add_argument("-o","--org", help="select org by name", dest="list_sub_command_orgs_list", type=list[str], action="append")
        list_parser.add_argument("-t", "--tlds", help="list tlds for selected orgs", action="store_true", dest="list_sub_command_ls_subs_tlds")
        list_parser.add_argument("-s", "--subs", help="list subdomains for selected orgs", action="store_true", dest="list_sub_command_ls_subs_domains")
        list_parser.add_argument("-a","--after", type=str, help="Start date in YYYY-MM-DD format", dest="list_sub_command_ls_subs_after_filter")
        list_parser.add_argument("-b","--before", type=str, help="End date in YYYY-MM-DD format", dest="list_sub_command_ls_subs_before_filter")

        # list_sub_parser = list_parser.add_subparsers(title="List Subcommands", dest="list_sub_command")
        # list_org_sub_parser = list_sub_parser.add_parser("orgs", help="List orgs present in DB")
        # list_org_sub_parser.add_argument()

        # display help, if no arguments are passed
        args = parser.parse_args(args=None if argv[1:] else ['--help'])
        logging.info(f"Arguments Passed - {args}")
        
        if args.subcommand == 'onboard':
            if args.host:
                logging.debug(f"Target Args passed - {args.host}")
                parsed_args['input_type'] = "host"
                parsed_args['input'] = str(args.host)
                
            # if '-f' option is chosen
            elif args.file_name:
                logging.debug(f"File Args passed - {args.file_name}")
                parsed_args['input_type'] = "file"
                parsed_args['input'] = str(args.file_name)

        if args.subcommand != "list":

            if args.aws_profiles:
                parsed_args["aws_profiles"] = args.aws_profiles.split(',')
            else:
                parsed_args["aws_profiles"] = ['default']

            if args.workflow:
                parsed_args['workflow'] = args.workflow
            else:
                parsed_args['workflow'] = 'default'

            parsed_args['org'] = args.org

            if args.app:
                parsed_args["app"] = args.app
            
            if args.passive:
                parsed_args["passive"] = True
            
            if args.stale:
                parsed_args["stale"] = True

            if args.ignore_stale:
                parsed_args["ignore_stale"] = True 
            
            if args.use_ray:
                parsed_args["use_ray"] = True
            
            if args.num_actors:
                parsed_args["num_actors"] = args.num_actors
            
            if args.delete_logs:
                parsed_args["delete_logs"] = args.delete_logs

            if args.verbose:
                parsed_args["verbose"] = True

            if args.thread_count:
                parsed_args["thread_count"] = args.thread_count
        
        if args.subcommand == "scan":
            if args.subdomain:
                parsed_args["subdomain"] = args.subdomain

        if args.subcommand == "onboard":
            if args.subdomain:
                parsed_args["subdomain"] = args.host

        if args.subcommand == "list":
            parsed_args["list_"] = True

            # python launch.py list -l
            if args.list_sub_command_ls_orgs:
                parsed_args["list_orgs"] = True

            # python launch.py list -d -s -t -o <org> -a 2024-10-04 -b 2024-10-05
            if args.list_sub_command_ls_domains:
                asset_types = []
                if args.list_sub_command_ls_subs_tlds:
                    asset_types.append("TLD")
                if args.list_sub_command_ls_subs_domains:
                    asset_types.append("subdomain")
                
                parsed_args["asset_types_list"] = asset_types
                parsed_args["orgs_list"] = [ ''.join(org) for org in args.list_sub_command_orgs_list]
                parsed_args["list_domains"] = True

                if args.list_sub_command_ls_subs_after_filter:
                    parsed_args["after_datetime_filter"] = f"{args.list_sub_command_ls_subs_after_filter}T00:00:00Z"

                if args.list_sub_command_ls_subs_before_filter:
                    parsed_args["before_datetime_filter"] = f"{args.list_sub_command_ls_subs_before_filter}T23:59:59Z"

        args_pydantic_obj = ArgsModel.parse_obj(parsed_args)
        logging.info(f'parsed args - {args_pydantic_obj}')
        logging.info(f"Parsing Arguements - Completed")

        return args_pydantic_obj

        