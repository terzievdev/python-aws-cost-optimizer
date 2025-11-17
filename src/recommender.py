import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json


class MLRecommender:
    """ML-powered recommendation engine using sklearn"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=3, random_state=42)

    def generate_ml_recommendations(self, scan_data):
        """Generate ML-based recommendations from usage patterns"""
        print(" Running ML analysis...")

        # Extract features from EC2 instances
        features = []
        instances = []

        for region, data in scan_data['regions'].items():
            for instance in data['ec2_instances']:
                if instance['state'] == 'running':
                    # Features: CPU avg, days running
                    launch_time = datetime.fromisoformat(instance['launch_time']) if instance[
                        'launch_time'] else datetime.now()
                    days_running = (datetime.now() - launch_time.replace(tzinfo=None)).days

                    features.append([
                        instance['cpu_avg_7d'],
                        days_running
                    ])
                    instances.append({
                        'region': region,
                        'instance_id': instance['instance_id'],
                        'type': instance['type'],
                        'cpu': instance['cpu_avg_7d'],
                        'days': days_running
                    })

        if len(features) < 3:
            print("️  Not enough data for ML clustering")
            return []

        # Normalize features
        features_scaled = self.scaler.fit_transform(features)

        # Cluster instances
        clusters = self.model.fit_predict(features_scaled)

        # Analyze clusters
        recommendations = []
        for cluster_id in range(3):
            cluster_instances = [instances[i] for i in range(len(instances)) if clusters[i] == cluster_id]

            if cluster_instances:
                avg_cpu = np.mean([inst['cpu'] for inst in cluster_instances])

                if avg_cpu < 10:
                    for inst in cluster_instances:
                        recommendations.append({
                            'type': 'ML_UNDERUTILIZED',
                            'severity': 'MEDIUM',
                            'region': inst['region'],
                            'resource_id': inst['instance_id'],
                            'cluster': f"Cluster {cluster_id}",
                            'recommendation': f"Instance in low-utilization cluster (avg {avg_cpu:.1f}% CPU)",
                            'action': 'CONSIDER_DOWNSIZING'
                        })

        print(f" ML generated {len(recommendations)} recommendations")
        return recommendations


from datetime import datetime

if __name__ == '__main__':
    import glob

    latest_scan = max(glob.glob('data/scans/*.json'), key=lambda x: x)

    with open(latest_scan, 'r') as f:
        scan_data = json.load(f)

    recommender = MLRecommender()
    ml_recs = recommender.generate_ml_recommendations(scan_data)

    print(f"\n ML Recommendations: {len(ml_recs)}")
    for rec in ml_recs[:3]:
        print(f"  - {rec['resource_id']}: {rec['recommendation']}")
