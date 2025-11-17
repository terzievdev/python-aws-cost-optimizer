import json
from datetime import datetime, timedelta
from config import EC2_HOURLY_COST, IDLE_CPU_THRESHOLD, IDLE_DAYS_THRESHOLD


class CostAnalyzer:
    """Analyzes costs and generates recommendations"""

    def __init__(self, scan_data):
        self.scan_data = scan_data
        self.recommendations = []
        self.potential_savings = 0.0

    def analyze(self):
        """Main analysis function"""
        print(" Starting cost analysis...")

        for region, data in self.scan_data['regions'].items():
            self.analyze_ec2_instances(region, data['ec2_instances'])
            self.analyze_ebs_volumes(region, data['ebs_volumes'])

        print(f" Analysis complete! Found {len(self.recommendations)} recommendations")
        print(f" Potential monthly savings: ${self.potential_savings:.2f}")

        return {
            'timestamp': datetime.now().isoformat(),
            'recommendations': self.recommendations,
            'total_potential_savings': round(self.potential_savings, 2)
        }

    def analyze_ec2_instances(self, region, instances):
        """Analyze EC2 instances for cost optimization"""
        for instance in instances:
            if instance['state'] != 'running':
                continue

            instance_type = instance['type']
            cpu_avg = instance['cpu_avg_7d']

            # Check if instance is idle
            if cpu_avg < IDLE_CPU_THRESHOLD:
                hourly_cost = EC2_HOURLY_COST.get(instance_type, 0.05)  # Default $0.05/hr
                monthly_savings = hourly_cost * 24 * 30

                self.recommendations.append({
                    'type': 'EC2_IDLE',
                    'severity': 'HIGH',
                    'region': region,
                    'resource_id': instance['instance_id'],
                    'resource_type': instance_type,
                    'issue': f"Instance has {cpu_avg}% average CPU (last 7 days)",
                    'recommendation': 'STOP instance during idle periods',
                    'action': 'STOP',
                    'monthly_savings': round(monthly_savings, 2),
                    'details': instance
                })

                self.potential_savings += monthly_savings

        print(f"   Analyzed {len(instances)} EC2 instances in {region}")

    def analyze_ebs_volumes(self, region, volumes):
        """Analyze EBS volumes for cost optimization"""
        for volume in volumes:
            if not volume['attached'] and volume['state'] == 'available':
                # Unattached volume costs ~$0.10/GB/month
                monthly_cost = volume['size_gb'] * 0.10

                self.recommendations.append({
                    'type': 'EBS_UNATTACHED',
                    'severity': 'MEDIUM',
                    'region': region,
                    'resource_id': volume['volume_id'],
                    'resource_type': f"EBS {volume['volume_type']}",
                    'issue': f"Volume ({volume['size_gb']} GB) unattached since creation",
                    'recommendation': 'DELETE unattached volume or create snapshot',
                    'action': 'SNAPSHOT_DELETE',
                    'monthly_savings': round(monthly_cost, 2),
                    'details': volume
                })

                self.potential_savings += monthly_cost

        print(f"   Analyzed {len(volumes)} EBS volumes in {region}")


if __name__ == '__main__':
    # Test with latest scan data
    import glob

    latest_scan = max(glob.glob('data/scans/*.json'), key=lambda x: x)

    with open(latest_scan, 'r') as f:
        scan_data = json.load(f)

    analyzer = CostAnalyzer(scan_data)
    results = analyzer.analyze()

    print(f"\n Recommendations: {len(results['recommendations'])}")
    for rec in results['recommendations'][:5]:  # Show first 5
        print(f"  - {rec['type']}: {rec['resource_id']} → Save ${rec['monthly_savings']}/mo")
