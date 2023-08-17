
import sys
import logging
from re import compile
from mantis.models.args_model import ArgsModel
from mantis.utils.asset_type import AssetType
from mantis.utils.common_utils import CommonUtils

class ListAssets:

    @staticmethod
    def list_assets(args: ArgsModel) -> list:

        INPUT_TYPE_FILE = "file"
        assets = []
        ip_range = []
        ip_subnet = []
        expanded_assets = []
        invalid_assets = []
        
        if args.input_type == INPUT_TYPE_FILE:
            assets = CommonUtils.parse_file(args.input)
        else:
            assets.append(args.input)
        
        # Special character validation on assets
        validated_assets = ListAssets.basic_input_validation(assets)
        logging.debug(f"List Assets: Assets post basic input validation - {validated_assets}")

        # Expand IP range
        for every_asset in validated_assets:
            if AssetType.check_ip_range(every_asset):
                expanded_assets = AssetType.expand_ip_range(every_asset)
                ip_range.append(every_asset)
            elif AssetType.check_ip_cidr_regex(every_asset):
                if AssetType.check_ip_cidr(every_asset):
                    expanded_assets = AssetType.expand_ip_cidr(every_asset)
                    ip_subnet.append(every_asset)
                else:
                    logging.warning(f'Invalid Asset Input - {every_asset}')
                    invalid_assets.append(every_asset)
            
        # Add expanded IP range to the assets
        if validated_assets:
            if expanded_assets:
                validated_assets = validated_assets + expanded_assets
                
                # Remove invalid inputs, subnets/ip ranges from existing list 
                if invalid_assets:
                    validated_assets = set(validated_assets) - set(invalid_assets)
                if ip_range:
                    validated_assets = set(validated_assets) - set(ip_range)
                elif ip_subnet:
                    validated_assets = set(validated_assets) - set(ip_subnet)

                # Remove duplicate assets
                validated_assets = list(set(validated_assets))
                logging.debug(f'List Assets: Validated Assets List - {validated_assets}')
        else:
            logging.exception(f'List Assets: No Valid assets provided to scan, Quitting !')
            sys.exit(1)
        
        return validated_assets
    

    
    @staticmethod
    def basic_input_validation(assets: list) -> list:
        logging.debug(f"Basic Input Validation: Assets - {assets}")
        args_regex = compile('[@_!#$%^&*()<>?\|}{~]')
        invalid_assets = []

        for asset in assets:
            if(args_regex.search(asset) is not None):
                logging.warning(f"Basic Input Validation: Invalid Asset - {asset}")
                invalid_assets.append(asset)
        valid_assets = set(assets) - set(invalid_assets)
        valid_assets = list(set(valid_assets))

        return valid_assets
