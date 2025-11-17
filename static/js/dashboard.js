// Dashboard functionality

async function loadDashboardData() {
    try {
        const response = await fetch('/api/latest-scan');
        const data = await response.json();

        if (data.error) {
            showStatus('No scan data available. Click "Run Manual Scan" to start.', 'error');
            return;
        }

        // Update metrics
        document.getElementById('total-ec2').textContent = data.summary.total_ec2_instances;
        document.getElementById('idle-ec2').textContent = data.summary.idle_ec2_instances;
        document.getElementById('unattached-ebs').textContent = data.summary.unattached_ebs_volumes;

        // Load recommendations for savings
        loadSavingsData();

        // Update scan time
        const scanTime = new Date(data.scan_time).toLocaleString();
        document.getElementById('scan-time').textContent = `Last scan: ${scanTime}`;

        // Display regions summary
        displayRegionsSummary(data.regions);

    } catch (error) {
        console.error('Error loading dashboard:', error);
        showStatus('Error loading dashboard data', 'error');
    }
}

async function loadSavingsData() {
    try {
        const response = await fetch('/api/latest-recommendations');
        const data = await response.json();

        if (!data.error) {
            document.getElementById('potential-savings').textContent =
                `$${data.total_potential_savings.toFixed(2)}`;
        }
    } catch (error) {
        console.error('Error loading savings:', error);
    }
}

function displayRegionsSummary(regions) {
    const container = document.getElementById('regions-summary');

    let html = '<div class="regions-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;">';

    for (const [region, data] of Object.entries(regions)) {
        const ec2Count = data.ec2_instances.length;
        const ebsCount = data.ebs_volumes.length;
        const rdsCount = data.rds_instances.length;

        html += `
            <div style="background: white; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color: #667eea; margin-bottom: 10px;">${region}</h4>
                <p>EC2: ${ec2Count} | EBS: ${ebsCount} | RDS: ${rdsCount}</p>
            </div>
        `;
    }

    html += '</div>';
    container.innerHTML = html;
}

async function triggerManualScan() {
    const button = document.getElementById('trigger-scan');
    button.disabled = true;
    button.textContent = ' Scanning...';

    showStatus('Scanning AWS resources across all regions...', 'success');

    try {
        const response = await fetch('/api/trigger-scan', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            showStatus(` Scan complete! Found ${result.recommendations_count} recommendations. Potential savings: $${result.potential_savings}/month`, 'success');
            loadDashboardData(); // Reload dashboard
        } else {
            showStatus(' Scan failed: ' + result.error, 'error');
        }
    } catch (error) {
        showStatus(' Error: ' + error.message, 'error');
    } finally {
        button.disabled = false;
        button.textContent = ' Run Manual Scan';
    }
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('status-message');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type} show`;

    setTimeout(() => {
        statusDiv.classList.remove('show');
    }, 5000);
}

// Event listeners
document.getElementById('trigger-scan').addEventListener('click', triggerManualScan);
document.getElementById('view-recommendations').addEventListener('click', () => {
    window.location.href = '/recommendations';
});

// Load dashboard on page load
loadDashboardData();

// Auto-refresh every 60 seconds
setInterval(loadDashboardData, 60000);
