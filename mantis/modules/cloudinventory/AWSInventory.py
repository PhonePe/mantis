import logging

from mantis.tool_base_classes.baseScanner import BaseScanner
from mantis.models.args_model import ArgsModel
from mantis.config_parsers.config_client import ConfigProvider
from mantis.utils.crud_utils import CrudUtils
from mantis.constants import CLOUD_PROVIDER_AWS
from mantis.modules.cloudinventory import build_cloud_asset

'''
AWSInventory collects public-facing AWS resources using boto3. Each AWS profile
is emitted as its own command tuple so accounts parallelize across Ray actors.

Configuration (local.yml):
  cloud.aws.profiles : list of named AWS profiles (falls back to args.aws_profiles)
  cloud.aws.regions  : list of regions (empty = all EC2-described regions)

Resources collected: EC2 instances (public IP), ELBv2 load balancers, RDS
instances (publicly accessible), and S3 buckets.
'''


class AWSInventory(BaseScanner):

    async def init(self, args: ArgsModel):
        self.args = args
        aws_config = ConfigProvider.get_config().cloud.aws
        profiles = aws_config.profiles or getattr(args, 'aws_profiles', None) or ['default']

        # One command tuple per profile (account) → parallelizes across Ray actors.
        tool_tuples = []
        for profile in profiles:
            inst = AWSInventory()
            inst.args = args
            inst.account = profile
            tool_tuples.append((inst, profile))
        return tool_tuples

    async def execute(self, tooltuple):
        results = {"success": 0, "failure": 0}
        profile = self.account
        logging.info(f"Collecting AWS inventory for profile: {profile}")

        try:
            import boto3
        except ImportError:
            msg = "boto3 package not installed"
            logging.error(msg)
            results["failure"] = 1
            results["exception"] = msg
            return results

        aws_config = ConfigProvider.get_config().cloud.aws

        cloud_assets = []
        try:
            try:
                session = boto3.Session(profile_name=profile)
            except Exception as e:
                msg = f"AWS profile '{profile}' unavailable: {e}"
                logging.warning(msg)
                results["failure"] = 1
                results["exception"] = msg
                return results

            account_id = self._get_account_id(session)
            regions = aws_config.regions or self._get_regions(session)

            self._collect_s3(session, account_id, cloud_assets)
            for region in regions:
                self._collect_ec2(session, region, account_id, cloud_assets)
                self._collect_elbv2(session, region, account_id, cloud_assets)
                self._collect_rds(session, region, account_id, cloud_assets)

            summary = await CrudUtils.sync_cloud_assets(
                CLOUD_PROVIDER_AWS, self.args.org, account_id, cloud_assets
            )
            results["success"] = 1
            results["output"] = (f"AWS[{profile}]: {summary['written']} synced, "
                                 f"{summary['created']} new, {summary['removed']} removed, "
                                 f"{summary['deactivated']} inactive")
            logging.info(results["output"])
        except Exception as e:
            logging.error(f"AWS inventory error ({profile}): {e}")
            results["failure"] = 1
            results["exception"] = str(e)

        return results

    def _get_account_id(self, session):
        try:
            return session.client('sts').get_caller_identity().get('Account')
        except Exception as e:
            logging.debug(f"Unable to resolve AWS account id: {e}")
            return None

    def _get_regions(self, session):
        try:
            ec2 = session.client('ec2', region_name='us-east-1')
            return [r['RegionName'] for r in ec2.describe_regions()['Regions']]
        except Exception as e:
            logging.warning(f"Unable to list AWS regions, defaulting to us-east-1: {e}")
            return ['us-east-1']

    def _collect_ec2(self, session, region, account_id, cloud_assets):
        try:
            ec2 = session.client('ec2', region_name=region)
            reservations = ec2.describe_instances().get('Reservations', [])
            for reservation in reservations:
                for instance in reservation.get('Instances', []):
                    public_ip = instance.get('PublicIpAddress')
                    public_dns = instance.get('PublicDnsName')
                    cloud_assets.append(build_cloud_asset(
                        provider=CLOUD_PROVIDER_AWS,
                        resource_id=instance['InstanceId'],
                        resource_type="EC2Instance",
                        org=self.args.org,
                        name=instance['InstanceId'],
                        account_id=account_id,
                        region=region,
                        is_public=bool(public_ip),
                        public_ips=[public_ip] if public_ip else [],
                        public_fqdns=[public_dns] if public_dns else [],
                        properties={"state": instance.get('State', {}).get('Name')},
                    ))
        except Exception as e:
            logging.debug(f"EC2 collection failed in {region}: {e}")

    def _collect_elbv2(self, session, region, account_id, cloud_assets):
        try:
            elb = session.client('elbv2', region_name=region)
            for lb in elb.describe_load_balancers().get('LoadBalancers', []):
                is_public = lb.get('Scheme') == 'internet-facing'
                dns = lb.get('DNSName')
                cloud_assets.append(build_cloud_asset(
                    provider=CLOUD_PROVIDER_AWS,
                    resource_id=lb['LoadBalancerArn'],
                    resource_type="LoadBalancer",
                    org=self.args.org,
                    name=lb.get('LoadBalancerName'),
                    account_id=account_id,
                    region=region,
                    is_public=is_public,
                    public_fqdns=[dns] if dns and is_public else [],
                    properties={"scheme": lb.get('Scheme'), "type": lb.get('Type')},
                ))
        except Exception as e:
            logging.debug(f"ELBv2 collection failed in {region}: {e}")

    def _collect_rds(self, session, region, account_id, cloud_assets):
        try:
            rds = session.client('rds', region_name=region)
            for db in rds.describe_db_instances().get('DBInstances', []):
                is_public = db.get('PubliclyAccessible', False)
                endpoint = db.get('Endpoint', {}).get('Address')
                cloud_assets.append(build_cloud_asset(
                    provider=CLOUD_PROVIDER_AWS,
                    resource_id=db['DBInstanceArn'],
                    resource_type="RDSInstance",
                    org=self.args.org,
                    name=db.get('DBInstanceIdentifier'),
                    account_id=account_id,
                    region=region,
                    is_public=is_public,
                    public_fqdns=[endpoint] if endpoint and is_public else [],
                    properties={"engine": db.get('Engine')},
                ))
        except Exception as e:
            logging.debug(f"RDS collection failed in {region}: {e}")

    def _collect_s3(self, session, account_id, cloud_assets):
        try:
            s3 = session.client('s3')
            for bucket in s3.list_buckets().get('Buckets', []):
                name = bucket['Name']
                is_public = self._is_bucket_public(s3, name)
                cloud_assets.append(build_cloud_asset(
                    provider=CLOUD_PROVIDER_AWS,
                    resource_id=f"s3:{name}",
                    resource_type="S3Bucket",
                    org=self.args.org,
                    name=name,
                    account_id=account_id,
                    region="global",
                    is_public=is_public,
                    properties={},
                ))
        except Exception as e:
            logging.debug(f"S3 collection failed: {e}")

    def _is_bucket_public(self, s3, name):
        try:
            status = s3.get_public_access_block(Bucket=name)
            config = status.get('PublicAccessBlockConfiguration', {})
            # public if any block setting is disabled
            return not all(config.get(k, False) for k in (
                'BlockPublicAcls', 'IgnorePublicAcls',
                'BlockPublicPolicy', 'RestrictPublicBuckets'))
        except Exception:
            # no block configuration usually means not restricted
            return True
