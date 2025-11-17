import boto3
from datetime import datetime


class RemediationExecutor:
    """Executes auto-remediation actions on AWS resources"""

    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.actions_taken = []

    def execute_recommendations(self, recommendations, auto_approve_threshold=20.0):
        """Execute recommendations automatically if savings < threshold"""
        print(f"  Executing recommendations (dry_run={self.dry_run})...")

        for rec in recommendations:
            if rec['monthly_savings'] < auto_approve_threshold:
                self.execute_single_recommendation(rec)

        print(f" Executed {len(self.actions_taken)} actions")
        return self.actions_taken

    def execute_single_recommendation(self, rec):
        """Execute a single recommendation"""
        action = rec['action']
        region = rec['region']
        resource_id = rec['resource_id']

        try:
            if action == 'STOP':
                result = self.stop_ec2_instance(region, resource_id)
            elif action == 'SNAPSHOT_DELETE':
                result = self.snapshot_and_delete_volume(region, resource_id)
            else:
                result = f"Unknown action: {action}"

            self.actions_taken.append({
                'timestamp': datetime.now().isoformat(),
                'recommendation': rec,
                'result': result,
                'success': True
            })

            print(f"   {action} on {resource_id}: {result}")

        except Exception as e:
            print(f"   Failed to {action} on {resource_id}: {e}")
            self.actions_taken.append({
                'timestamp': datetime.now().isoformat(),
                'recommendation': rec,
                'error': str(e),
                'success': False
            })

    def stop_ec2_instance(self, region, instance_id):
        """Stop an EC2 instance"""
        if self.dry_run:
            return f"[DRY RUN] Would stop instance {instance_id}"

        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.stop_instances(InstanceIds=[instance_id])
        return f"Stopped instance {instance_id}"

    def snapshot_and_delete_volume(self, region, volume_id):
        """Create snapshot then delete EBS volume"""
        if self.dry_run:
            return f"[DRY RUN] Would snapshot and delete volume {volume_id}"

        ec2 = boto3.client('ec2', region_name=region)

        # Create snapshot
        snapshot = ec2.create_snapshot(
            VolumeId=volume_id,
            Description=f"Auto-backup before deletion - {datetime.now().isoformat()}"
        )
        snapshot_id = snapshot['SnapshotId']


        return f"Created snapshot {snapshot_id}, ready to delete {volume_id}"


if __name__ == '__main__':
    executor = RemediationExecutor(dry_run=True)

    test_rec = {
        'action': 'STOP',
        'region': 'us-east-1',
        'resource_id': 'i-test123',
        'monthly_savings': 15.0
    }

    executor.execute_single_recommendation(test_rec)
    print(f"\n Actions taken: {len(executor.actions_taken)}")
