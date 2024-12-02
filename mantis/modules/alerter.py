from mantis.config_parsers.config_client import ConfigProvider
from mantis.utils.notifications import NotificationsUtils, Notifications
from mantis.db.crud_assets import read_assets
from mantis.db.crud_vulnerabilities import read_findings
from datetime import datetime
import logging
import copy
import sys
from time import sleep

class Alerter:
    @staticmethod
    async def send_alerts(log_dict, args):
        try:
            notify_config = ConfigProvider.get_config().notify
            if log_dict is not None:
                scan_efficiency_blocks, scan_stats, module_scan_stats = Alerter.get_stats_slack_message(log_dict)
            
            for team in notify_config:
                asset_type_list, asset_tag_list = NotificationsUtils.get_assets_to_notify_list(team.teamName)
                finding__type_list, finding_tag_list = NotificationsUtils.get_findings_to_notify_list(team.teamName)
                assets, findings = await Alerter.fetch_results(asset_types=asset_type_list, finding_types=finding__type_list, args=args, app=team.app)
                slack_blocks = await Alerter.get_inventory_slack_message(assets, findings, asset_tag_list, finding_tag_list)
                for channel_type in team.channel:
                    if channel_type == 'slack':
                        if isinstance(team.channel[channel_type], list):
                            for webhook in team.channel[channel_type]:
                                if team.scanEfficiency == True:
                                    Notifications.send_slack_notifications(scan_efficiency_blocks, webhook)
                                # for block in slack_blocks:
                                
                                Notifications.send_slack_notifications(slack_blocks, webhook)
                        else:
                            logging.error("Slack must provide list of webhooks, check local.yml")
                    if channel_type == 'mattermost':
                        if isinstance(team.channel[channel_type], list):
                            for webhook in team.channel[channel_type]:
                                if team.scanEfficiency == True:
                                    Notifications.send_mattermost_notifications(scan_efficiency_blocks, webhook)
                                Notifications.send_mattermost_notifications(slack_blocks, webhook)
                        else:
                            logging.error("Mattermost must provide a list of webhooks, check local.yml")
                            
        except Exception as e:
            logging.debug(f"Slack alerts not configured: {e}")
        return scan_stats, module_scan_stats

    @staticmethod
    async def get_inventory_slack_message(assets, findings, asset_tag_list, finding_tag_list):
        blocks = []
        section = {
                "type": "section",
                "text": {
                "type": "mrkdwn",
                "text": ""
                }
            }
    
        divider = {"type": "divider"}
        total_new_assets = 0
        if len(assets):
            assets_section = copy.deepcopy(section)
            assets_section["text"]["text"] = "*NEW ASSETS*"
            blocks.append(assets_section)
            # assets_section = copy.deepcopy(section)
            # assets_section["text"]["text"] = f"Count: {len(assets)}"
            # blocks.append(assets_section)
            for asset_type in assets:
                asset_type_section = copy.deepcopy(section)
                asset_type_section["text"]["text"] = f"_{asset_type['_id'].upper()}_:"
                
                if asset_type["_id"] in asset_tag_list:
                    for users in asset_tag_list[asset_type["_id"]]:
                        asset_type_section["text"]["text"] += f" <@{users}>"
                blocks.append(asset_type_section)
                if 'asset_info' in asset_type:
                    asset_section = copy.deepcopy(section)
                    for asset in asset_type['asset_info']:
                        total_new_assets += 1
                        asset_section["text"]["text"] += f"• {asset['asset']}"
                        if 'dns_names' in asset:
                            asset_section["text"]["text"] += f"| {asset['dns_names']}\t"
                        if 'friendly_name' in asset:
                            asset_section["text"]["text"] += f"| {asset['friendly_name']}"
                        asset_section["text"]["text"] += '\n'
                    blocks.append(asset_section)
            total_new_assets_count = copy.deepcopy(section)
            total_new_assets_count["text"]["text"] = f"Total New Assets Discovered: {total_new_assets}"
            blocks.append(total_new_assets_count)
        # else:
        #     assets_section = copy.deepcopy(section)
        #     assets_section["text"]["text"] = "*No new assets found*"
        #     blocks.append(assets_section)
            blocks.append(divider)

        total_new_findings = 0
        if len(findings):
            findings_section = copy.deepcopy(section)
            findings_section["text"]["text"] = "*NEW FINDINGS*"
            blocks.append(findings_section)
            # findings_section = copy.deepcopy(section)
            # findings_section["text"]["text"] = f"Count: {len(findings)}"
            # blocks.append(findings_section)
            for finding in findings:
                finding_section = copy.deepcopy(section)
                finding_section["text"]["text"] = f"_{finding['_id'].upper()}_:\n"
                if finding["_id"] in finding_tag_list:
                    for users in finding_tag_list[asset_type["_id"]]:
                        asset_type_section["text"]["text"] += f" <@{users}>"
                for info in finding['findings_info']:
                    total_new_findings += 1
                    if finding['_id'] == 'secret':
                        if "url" in info and info["host"] is not None:
                            finding_section["text"]["text"] += f"• <{info['url']}|{info['info']['key']}>\t\n"
                    else:
                        if "title" in info and info['title'] is not None:
                            finding_section["text"]["text"] += f"• {info['title']}\t"
                        if "host" in info and info["host"] is not None:
                            finding_section["text"]["text"] += f"{info['host']}\t"
                        finding_section["text"]["text"] += '\n'
                    ## elif add status code. 
                blocks.append(finding_section)
            total_new_findings_count = copy.deepcopy(section)
            total_new_findings_count["text"]["text"] = f"Total New Findings Discovered: {total_new_findings}"
            blocks.append(total_new_findings_count)
        # else:
        #     findings_section = copy.deepcopy(section)
        #     findings_section["text"]["text"] = "*No new findings found*"
        #     blocks.append(findings_section)

        
        return blocks

    @staticmethod
    async def fetch_results(asset_types, finding_types, args, app):
        assets = await Alerter.get_assets_by_type_discovered(asset_types=asset_types, args=args, app=app)      
        findings = await Alerter.get_findings_by_type_discovered(finding_types=finding_types, args=args, app=app)
        return assets,findings    

    @staticmethod
    async def get_assets_by_type_discovered(asset_types, args, app):
        pipeline_type_discovered = []
        if len(app):
            pipeline_type_discovered.append({"$match" : {
                "app" : { "$in" : app}
            }}
            )
        if args is not None:
            pipeline_type_discovered.append({"$match" : {
               "org" : args.org
            }}
            )
        pipeline_type_discovered.extend([
            
            {"$match" : {
                "asset_type": { "$in": asset_types}
            }},
            {"$match" : {"created_timestamp":{"$gte" : datetime.today().strftime('%Y-%m-%d')}}},
            {"$group":  {
                "_id": "$asset_type",
                "asset_info":{"$push":{
                            "asset": "$asset",
                            "dns_names": "$others.dns_names",
                            "friendly_name": "$others.issuer.friendly_name"
                    }
                }
                }
            }
        ])

        assets = await read_assets(pipeline_type_discovered)
        if assets:
            return assets
        else:
            return []
    
    @staticmethod
    async def get_findings_by_type_discovered(finding_types, args, app):
        pipeline_type_discovered = []
        if len(app):
            pipeline_type_discovered.append({"$match" : {
                "app" : { "$in" : app}
            }}
            )
        if args is not None:
            pipeline_type_discovered.append({"$match" : {
               "org" : args.org
            }}
            )
        pipeline_type_discovered.extend([

            {"$match" : {
                "type": { "$in": finding_types }
            }},
            {"$match" : {"created_timestamp":{"$gte" : datetime.today().strftime('%Y-%m-%d')}}},
            {"$group":  {
                "_id": "$type",
                "findings_info" : {
                    "$push": {
                        "title" : "$title",
                        "host": "$host" ,
                        "info": "$info",
                        "url": "$url"}
                    }
                }
            }
        ])

        findings = await read_findings(pipeline_type_discovered)
        if findings:
            return findings
        else:
            return []


    @staticmethod
    def get_stats_slack_message(logs):
        scan_stats = {}
        scan_stats["scan_start"] = logs.scan_start_time
        scan_stats["scan_end"] = logs.scan_end_time
        scan_stats["scan_time_taken"] = logs.scan_time_taken
        scan_stats["scan_percentage"] = 0
        no_scan_efficiency_modules = 0
        module_scan_stats_list = []
        for modules in logs.scan_modules_logs:
            module_scan_stats = {}
            module_scan_stats["module_name"] = modules.module_name
            module_scan_stats["module_time_taken"] = modules.module_time_taken
            success = 0
            failure = 0
            if modules.module_tool_logs != None:
                for assetLogs in modules.module_tool_logs:
                    success += assetLogs.success
                    failure += assetLogs.failure
            else:
                no_scan_efficiency_modules += 1
                
            if success + failure != 0:
                module_scan_stats["module_efficiency"] = 100 * success/(success + failure)
            else:
                module_scan_stats["module_efficiency"] = 0

            scan_stats["scan_percentage"] += module_scan_stats["module_efficiency"]

            module_scan_stats_list.append(module_scan_stats)
        scan_stats["scan_percentage"]  = scan_stats["scan_percentage"]/ (len(logs.scan_modules_logs) - no_scan_efficiency_modules)

                
        blocks = []
        section = {
                "type": "section",
                "text": {
                "type": "mrkdwn",
                "text": ""
                }
            }
    
        divider = {"type": "divider"}
        ### Scan STATS section
        scan_stats_section = copy.deepcopy(section)
        scan_stats_section["text"]["text"] = "*SCAN STATS:*"
        blocks.append(scan_stats_section)
        command_executed_section = copy.deepcopy(section)
        command_executed_section["text"]["text"] = f"*Command Executed*: `python3 {' '.join(sys.argv)}`"
        blocks.append(command_executed_section)
        scan_stats_section = copy.deepcopy(section)
        scan_stats_section["text"]["text"] = f"•Scan Efficiency: {scan_stats['scan_percentage']}%\n"
        scan_stats_section["text"]["text"] += f"•Scan Started: {scan_stats['scan_start']}\n"
        scan_stats_section["text"]["text"] += f"•Scan Ended: {scan_stats['scan_end']}\n"
        scan_stats_section["text"]["text"] += f"•Scan Time Taken: {scan_stats['scan_time_taken']}\n"
        blocks.append(scan_stats_section)

        blocks.append(divider)

        for module in module_scan_stats_list:
            module_section = copy.deepcopy(section)
            module_section["text"]["text"] = f"_{module['module_name'].upper()}_:\n• Scan Efficiency: {str(module['module_efficiency'])}%\n• Time Taken: {module['module_time_taken']} \n"
            blocks.append(module_section)
            # for tool in results_dict[module]['tools_dict']:
            #     final_str += f"- {tool}\t Success %: {results_dict[module]['tools_dict'][tool]['success_percentage']}\n"
            # final_str += '\n'   
        blocks.append(divider)
        return blocks, scan_stats, module_scan_stats_list
