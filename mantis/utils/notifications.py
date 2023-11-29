import logging
from slack_sdk.webhook import WebhookClient
from mantis.config_parsers.config_client import ConfigProvider

class Notifications:
    
    @staticmethod
    def send_slack_notifications(blocks, webhook):
        if webhook == 'None':
            raise Exception("Slack URL not provided")
        webhook = WebhookClient(webhook)
        if blocks:
            response = webhook.send(text="Mantis notification",
                blocks=blocks
            )
        
        logging.debug(response.status_code)

class NotificationsUtils:

    @staticmethod
    def get_assets_to_notify_list(teamName):
        asset_list = []
        asset_tag_list = {}
        for team in ConfigProvider.get_config().notify:
            if team.teamName == teamName:
                for asset in team.assets:
                    if isinstance(asset,dict):
                        asset_tag_list.update(asset)
                        asset_list.append(list(asset.keys())[0])
                    elif isinstance(asset,str):
                        asset_list.append(asset)
                        
        return asset_list,asset_tag_list

    @staticmethod
    def get_findings_to_notify_list(teamName):
        findings_list = []
        finding_tag_list = []
        for team in ConfigProvider.get_config().notify:
            if team.teamName == teamName:
                for finding_type in team.findings:
                    if isinstance(finding_type,dict):
                        finding_tag_list.append(finding_type)
                        findings_list.append(list(finding_type.keys())[0])
                    elif isinstance(finding_type,str):
                        findings_list.append(finding_type)

        return findings_list,finding_tag_list