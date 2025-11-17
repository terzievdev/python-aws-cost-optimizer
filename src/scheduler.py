from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from src.scanner import AWSResourceScanner
from src.analyzer import CostAnalyzer
from src.recommender import MLRecommender
from src.executor import RemediationExecutor
import json
from config import SCAN_SCHEDULE_HOUR, RECOMMENDATIONS_DIR, get_timestamp


class CostOptimizerScheduler:
    """Scheduled jobs for daily AWS scans and optimizations"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()

    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Daily scan at 2 AM
        self.scheduler.add_job(
            self.daily_scan_and_optimize,
            'cron',
            hour=SCAN_SCHEDULE_HOUR,
            minute=0,
            id='daily_scan'
        )

        print(f" Scheduled daily scan at {SCAN_SCHEDULE_HOUR}:00")

    def daily_scan_and_optimize(self):
        """Main scheduled job - scan, analyze, recommend, execute"""
        print(f"\n{'=' * 60}")
        print(f" Starting scheduled AWS optimization job")
        print(f"{'=' * 60}\n")

        try:
            # Step 1: Scan resources
            scanner = AWSResourceScanner()
            scan_results = scanner.scan_all_regions()

            # Step 2: Analyze costs
            analyzer = CostAnalyzer(scan_results)
            analysis = analyzer.analyze()

            # Step 3: ML recommendations
            ml_recommender = MLRecommender()
            ml_recs = ml_recommender.generate_ml_recommendations(scan_results)

            # Combine recommendations
            all_recommendations = analysis['recommendations'] + ml_recs

            # Step 4: Execute safe actions (dry_run=False in production)
            executor = RemediationExecutor(dry_run=True)
            actions = executor.execute_recommendations(all_recommendations)

            # Save report
            report = {
                'timestamp': datetime.now().isoformat(),
                'scan_summary': scan_results['summary'],
                'total_recommendations': len(all_recommendations),
                'potential_savings': analysis['total_potential_savings'],
                'recommendations': all_recommendations,
                'actions_taken': actions
            }

            report_file = f"{RECOMMENDATIONS_DIR}/report_{get_timestamp()}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            print(f"\n Optimization job complete!")
            print(f" Report saved: {report_file}")
            print(f" Potential savings: ${analysis['total_potential_savings']:.2f}/month")

        except Exception as e:
            print(f" Error in scheduled job: {e}")

    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        print(" Scheduler started!")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print(" Scheduler stopped!")


if __name__ == '__main__':
    scheduler = CostOptimizerScheduler()
    scheduler.start()

    # Keep running
    try:
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
