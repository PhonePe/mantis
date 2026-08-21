import json
import logging

'''
Lightweight cloud inventory change events. Diffs detected during a sync are
emitted as structured `cloud.changed` records (change types: created, modified,
removed). Currently written to the log stream; the single emit() entry point can
later be extended to publish to a webhook, queue, or the alerter.
'''

EVENT_NAME = "cloud.changed"


class CloudEvents:

    @staticmethod
    def emit(change_type: str, resource: dict, org: str, changes: dict = None):
        payload = {
            "event": EVENT_NAME,
            "type": change_type,  # created | modified | removed
            "org": org,
            "provider": resource.get("provider"),
            "account_id": resource.get("account_id"),
            "resource_id": resource.get("resource_id"),
            "resource_type": resource.get("resource_type"),
            "name": resource.get("name"),
            "is_public": resource.get("is_public"),
        }
        if changes:
            payload["changes"] = changes
        logging.info(f"{EVENT_NAME} {json.dumps(payload)}")
