import logging
from mantis.models.args_model import ArgsModel
from mantis.utils.deboard_utils import deboard_organisation

class DeboardWorkflow:
    @staticmethod
    async def executor(args: ArgsModel):
        """
        Executes the deboarding process for a given organisation based on provided arguments.
        Deletes data from assets, findings, and extended assets collections accordingly.
        """
        if args.org:
            logging.info(f"Starting deboard process for organisation {args.org}")

            deboard = await deboard_organisation(args)

            if (deboard):
                logging.info(f"Successfully completed deboard process for organisation {args.org}")
                print(f"\n\033[1;32mAll specified data for {args.org} has been successfully deleted from the database\033[0m\n")
            else:
                logging.info(f"Deboard process completed for organisation {args.org}, but no matching records were found")
                print(f"\n\033[1;32mNo matching records found for {args.org}, Nothing was deleted\033[0m\n")
