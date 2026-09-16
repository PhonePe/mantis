from mantis.constants import ASSET_TYPE_CLOUD_RESOURCE


def build_cloud_asset(provider, resource_id, resource_type, org, name=None,
                      account_id=None, region=None, is_public=False,
                      public_ips=None, public_fqdns=None, risk_level=None,
                      properties=None):
    """Normalize a provider resource into a cloud_assets_collection document."""
    return {
        "_id": f"{provider}:{resource_id}",
        "provider": provider,
        "resource_id": resource_id,
        "resource_type": resource_type,
        "name": name,
        "org": org,
        "account_id": account_id,
        "region": region,
        "is_public": is_public,
        "public_ips": public_ips or [],
        "public_fqdns": public_fqdns or [],
        "risk_level": risk_level or ("high" if is_public else "low"),
        "properties": properties or {},
        "is_active": True,
    }
