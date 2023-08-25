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

        \033[0;32mmantis onboard -o example_org -t www.example.org\033[0m
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
    def args_parse() -> ArgsModel:
        parsed_args = {}

        parser = ArgumentParser(
                                prog='mantis',
                                formatter_class=CustomFormatter,
                                add_help=False,
                                usage=ArgsParse.msg()
                              )
        
        subparser = parser.add_subparsers(title="subparser", dest="subcommand")
        
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
        
        onboard_parser.add_argument('-r', '--use_ray', 
                            dest = 'use_ray',
                            help = 'use ray framework for distributed scans',
                            action = 'store_true' 
                            )
        
        onboard_parser.add_argument('-n', '--num_actors', 
                            dest = 'num_actors',
                            help = 'number of ray actors, default 10',
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
        
        scan_parser.add_argument('-r', '--use_ray', 
                            dest = 'use_ray',
                            help = 'use ray framework for distributed scans',
                            action = 'store_true' 
                            )
        
        scan_parser.add_argument('-n', '--num_actors', 
                            dest = 'num_actors',
                            help = 'number of ray actors, default 10',
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

            if args.aws_profiles:
                parsed_args["aws_profiles"] = args.aws_profiles.split(',')
            else:
                parsed_args["aws_profiles"] = ['default']


        if args.workflow:
            parsed_args['workflow'] = args.workflow
        else:
            parsed_args['workflow'] = 'default'

        parsed_args['org'] = args.org

        # if args.output:
        #     parsed_args["output"] = args.output
        # else:
        #     parsed_args["output"] = os.getcwd()
        
        if args.app:
            parsed_args["app"] = args.app
        
        if args.passive:
            parsed_args["passive"] = True
        
        if args.stale:
            parsed_args["stale"] = True

        # if args.aws_profiles:
        #     parsed_args["aws_profiles"] = args.aws_profiles
        #     print(parsed_args["aws_profiles"])

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
         

        args_pydantic_obj = ArgsModel.parse_obj(parsed_args)
        logging.info(f'parsed args - {args_pydantic_obj}')
        logging.info(f"Parsing Arguements - Completed")

        return args_pydantic_obj

        

    
    
   
