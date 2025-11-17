import boto3
import json
from datetime import datetime, timedelta
from config import AWS_REGIONS, SCAN_DATA_DIR, get_timestamp


class AWSResourceScanner:
    """Scans AWS resources across all regions"""

    def __init__(self):
        self.results = {
            'scan_time': datetime.now().isoformat(),
            'regions': {},
            'summary': {}
        }

    def scan_all_regions(self):
        """Scan EC2, EBS, RDS in all regions"""
        print(f" Starting multi-region AWS scan...")

        for region in AWS_REGIONS:
            print(f" Scanning region: {region}")
            self.results['regions'][region] = {
                'ec2_instances': self.scan_ec2_instances(region),
                'ebs_volumes': self.scan_ebs_volumes(region),
                'rds_instances': self.scan_rds_instances(region),
            }

        self.calculate_summary()
        self.save_results()
        return self.results

    def scan_ec2_instances(self, region):
        """Scan EC2 instances with CPU metrics"""
        try:
            ec2 = boto3.client('ec2', region_name=region)
            cloudwatch = boto3.client('cloudwatch', region_name=region)

            response = ec2.describe_instances()
            instances = []

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    state = instance['State']['Name']

                    # Get CPU utilization from CloudWatch
                    cpu_avg = self.get_cpu_utilization(cloudwatch, instance_id)

                    instances.append({
                        'instance_id': instance_id,
                        'type': instance.get('InstanceType', 'unknown'),
                        'state': state,
                        'launch_time': instance.get('LaunchTime').isoformat() if instance.get('LaunchTime') else None,
                        'cpu_avg_7d': cpu_avg,
                        'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    })

            print(f"   Found {len(instances)} EC2 instances in {region}")
            return instances

        except Exception as e:
            print(f"   Error scanning EC2 in {region}: {e}")
            return []

    def get_cpu_utilization(self, cloudwatch, instance_id):
        """Get average CPU utilization for last 7 days"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)

            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=['Average']
            )

            if response['Datapoints']:
                avg_cpu = sum(dp['Average'] for dp in response['Datapoints']) / len(response['Datapoints'])
                return round(avg_cpu, 2)
            return 0.0

        except Exception as e:
            print(f"    ️  Could not get CPU for {instance_id}: {e}")
            return 0.0

    def scan_ebs_volumes(self, region):
        """Scan EBS volumes (especially unattached ones)"""
        try:
            ec2 = boto3.client('ec2', region_name=region)
            response = ec2.describe_volumes()

            volumes = []
            for volume in response['Volumes']:
                volumes.append({
                    'volume_id': volume['VolumeId'],
                    'size_gb': volume['Size'],
                    'state': volume['State'],
                    'attached': len(volume.get('Attachments', [])) > 0,
                    'create_time': volume['CreateTime'].isoformat(),
                    'volume_type': volume.get('VolumeType', 'unknown')
                })

            print(f"   Found {len(volumes)} EBS volumes in {region}")
            return volumes

        except Exception as e:
            print(f"   Error scanning EBS in {region}: {e}")
            return []

    def scan_rds_instances(self, region):
        """Scan RDS instances"""
        try:
            rds = boto3.client('rds', region_name=region)
            response = rds.describe_db_instances()

            instances = []
            for db in response['DBInstances']:
                instances.append({
                    'db_identifier': db['DBInstanceIdentifier'],
                    'db_class': db['DBInstanceClass'],
                    'engine': db['Engine'],
                    'status': db['DBInstanceStatus'],
                    'allocated_storage': db.get('AllocatedStorage', 0),
                    'multi_az': db.get('MultiAZ', False)
                })

            print(f"   Found {len(instances)} RDS instances in {region}")
            return instances

        except Exception as e:
            print(f"   Error scanning RDS in {region}: {e}")
            return []

    def calculate_summary(self):
        """Calculate summary statistics"""
        total_ec2 = 0
        total_ebs = 0
        total_rds = 0
        idle_ec2 = 0
        unattached_ebs = 0

        for region_data in self.results['regions'].values():
            ec2_list = region_data['ec2_instances']
            total_ec2 += len(ec2_list)
            idle_ec2 += sum(1 for inst in ec2_list if inst['cpu_avg_7d'] < 5.0 and inst['state'] == 'running')

            ebs_list = region_data['ebs_volumes']
            total_ebs += len(ebs_list)
            unattached_ebs += sum(1 for vol in ebs_list if not vol['attached'])

            total_rds += len(region_data['rds_instances'])

        self.results['summary'] = {
            'total_ec2_instances': total_ec2,
            'idle_ec2_instances': idle_ec2,
            'total_ebs_volumes': total_ebs,
            'unattached_ebs_volumes': unattached_ebs,
            'total_rds_instances': total_rds
        }

    def save_results(self):
        """Save scan results to JSON file"""
        filename = f"{SCAN_DATA_DIR}/scan_{get_timestamp()}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n Scan results saved to: {filename}")
        return filename


if __name__ == '__main__':
    scanner = AWSResourceScanner()
    results = scanner.scan_all_regions()
    print(f"\n Scan complete! Summary: {json.dumps(results['summary'], indent=2)}")
