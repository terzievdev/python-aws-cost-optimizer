from flask import Flask, render_template, jsonify, request
import json
import glob
import os
from datetime import datetime
from src.scanner import AWSResourceScanner
from src.analyzer import CostAnalyzer
from src.recommender import MLRecommender
from src.executor import RemediationExecutor
from config import FLASK_HOST, FLASK_PORT, SECRET_KEY, SCAN_DATA_DIR, RECOMMENDATIONS_DIR

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = SECRET_KEY


@app.route('/')
def index():
    """Homepage - Dashboard"""
    return render_template('index.html')


@app.route('/api/latest-scan')
def get_latest_scan():
    """API: Get latest scan results"""
    try:
        scan_files = glob.glob(f'{SCAN_DATA_DIR}/*.json')
        if not scan_files:
            return jsonify({'error': 'No scan data available'}), 404

        latest_scan = max(scan_files, key=os.path.getctime)
        with open(latest_scan, 'r') as f:
            data = json.load(f)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/latest-recommendations')
def get_latest_recommendations():
    """API: Get latest recommendations"""
    try:
        rec_files = glob.glob(f'{RECOMMENDATIONS_DIR}/*.json')
        if not rec_files:
            return jsonify({'error': 'No recommendations available'}), 404

        latest_rec = max(rec_files, key=os.path.getctime)
        with open(latest_rec, 'r') as f:
            data = json.load(f)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trigger-scan', methods=['POST'])
def trigger_scan():
    """API: Trigger manual scan"""
    try:
        print(" Manual scan triggered via API")

        scanner = AWSResourceScanner()
        results = scanner.scan_all_regions()

        analyzer = CostAnalyzer(results)
        analysis = analyzer.analyze()

        return jsonify({
            'success': True,
            'message': 'Scan completed',
            'summary': results['summary'],
            'recommendations_count': len(analysis['recommendations']),
            'potential_savings': analysis['total_potential_savings']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/execute-action', methods=['POST'])
def execute_action():
    """API: Execute a specific recommendation"""
    try:
        rec = request.json
        executor = RemediationExecutor(dry_run=False)  # REAL execution
        executor.execute_single_recommendation(rec)

        return jsonify({
            'success': True,
            'message': f"Executed {rec['action']} on {rec['resource_id']}"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/recommendations')
def recommendations_page():
    """Recommendations page"""
    return render_template('recommendations.html')


if __name__ == '__main__':
    print(f" Starting Flask dashboard on http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
