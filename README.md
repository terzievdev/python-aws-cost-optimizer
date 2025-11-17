Python AWS Infrastructure Automator
An automated system for AWS cost optimization through ML-powered analysis and auto-remediation.

📋 Project Overview
This project is a production-ready cost optimization tool for AWS infrastructure that:

🔍 Scans EC2, EBS, and RDS resources across all AWS regions

💰 Analyzes costs and detects idle/underutilized resources

🤖 ML Engine for usage prediction and intelligent recommendations

⚙️ Auto-remediation – automatically stops idle instances, deletes unused volumes

📊 Flask Dashboard – real-time cost tracking, charts, approve/reject actions

📅 Scheduler – daily scans and email reports

🎯 Features
1. Multi-Region Resource Scanner
Scans 6 AWS regions simultaneously (US, EU, APAC)

Collects metrics from CloudWatch (7-day CPU utilization average)

Detects: running instances, unattached volumes, RDS databases

2. Cost Analyzer
Calculates potential monthly savings for each resource

Thresholds:

CPU < 5% for 7 days = IDLE

EBS unattached > 30 days = DELETE candidate

Uses real-time pricing from AWS Price List API

3. ML Recommendation Engine
K-Means clustering of instances by usage patterns

Scikit-learn model for underutilization detection

Predictive recommendations: "Downsize from t3.medium → t3.small"

4. Auto-Remediation Executor
Dry-run mode for testing (default)

Production mode – real AWS API calls

Actions: STOP instances, SNAPSHOT + DELETE volumes

Safety: auto-approve only for savings < $20/month

5. Flask Web Dashboard
Real-time metrics: total instances, idle count, monthly savings

Interactive charts (cost trends)

Approve/Reject recommendations with 1 click

API endpoints for external integration

6. Scheduled Jobs (APScheduler)
Daily scan at 2 AM

Auto-generate reports → JSON files

Email notifications (SNS/SES integration ready)

🏗️ Architecture
┌─────────────────────────────────────────────────────────────┐
│                     Flask Web Dashboard                      │
│              (0.0.0.0:5000 - Public Access)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        v                v                v
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Scanner    │  │   Analyzer   │  │  Executor    │
│   (boto3)    │  │  (pandas)    │  │  (boto3)     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       v                 v                 v
┌─────────────────────────────────────────────────────┐
│              AWS Services (Multi-Region)            │
│  EC2 | EBS | RDS | CloudWatch | Cost Explorer      │
└─────────────────────────────────────────────────────┘

📁 File Structure
python-aws-cost-optimizer/
├── src/
│   ├── scanner.py          # AWS resource scanner (boto3)
│   ├── analyzer.py         # Cost analysis engine
│   ├── recommender.py      # ML recommendation engine (sklearn)
│   ├── executor.py         # Auto-remediation engine
│   ├── scheduler.py        # APScheduler background jobs
│   └── app.py              # Flask web dashboard
├── templates/
│   ├── index.html          # Dashboard homepage
│   └── recommendations.html # Recommendations list
├── static/
│   ├── css/style.css

