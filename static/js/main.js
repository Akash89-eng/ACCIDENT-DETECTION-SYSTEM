// main.js - Premium Frontend Logic
let socket = null;
let detectionActive = false;
let videoStream = null;
let mediaRecorder = null;

// Initialize Socket.IO connection
function initSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to server');
        showNotification('Connected to detection system', 'success');
    });
    
    socket.on('accident_alert', (data) => {
        console.log('Accident detected:', data);
        showAccidentAlert(data);
        loadEvidence();
    });
    
    socket.on('realtime_accident', (data) => {
        showAccidentAlert(data);
        updateDetectionStatus(data);
    });
    
    socket.on('video_accident_alert', (data) => {
        showAccidentAlert(data);
        showNotification(`Accident detected in video! Severity: ${data.severity}`, 'danger');
    });
    
    socket.on('video_processing_complete', (data) => {
        showNotification(`Video processing complete: ${data.video}`, 'success');
        document.getElementById('upload-status').innerHTML = '<div class="alert alert-success">Processing complete!</div>';
    });
}

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const stats = await response.json();
        
        document.getElementById('total-accidents').textContent = stats.total_accidents;
        document.getElementById('active-alerts').textContent = stats.active_alerts;
        document.getElementById('total-vehicles').textContent = stats.total_vehicles;
        document.getElementById('total-evidence').textContent = stats.total_evidence;
        
        // Load recent accidents
        const recentList = document.getElementById('recent-accidents-list');
        if (stats.recent_accidents && stats.recent_accidents.length > 0) {
            recentList.innerHTML = stats.recent_accidents.map(acc => `
                <div class="alert alert-${acc.severity === 'CRITICAL' ? 'danger' : acc.severity === 'MAJOR' ? 'warning' : 'info'}">
                    <strong>${new Date(acc.timestamp).toLocaleString()}</strong><br>
                    Severity: ${acc.severity} | Confidence: ${acc.confidence}%<br>
                    ${acc.license_plate ? `Vehicle: ${acc.license_plate}` : ''}
                </div>
            `).join('');
        } else {
            recentList.innerHTML = '<div class="text-center">No recent accidents</div>';
        }
        
        // Update charts
        updatePerformanceChart();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Update performance chart
function updatePerformanceChart() {
    const ctx = document.getElementById('performance-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Detection Accuracy (%)',
                data: [92, 93, 94, 94.2],
                borderColor: '#4cc9f0',
                backgroundColor: 'rgba(76, 201, 240, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

// Start real-time detection
async function startDetection() {
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        const videoElement = document.getElementById('video-feed');
        videoElement.srcObject = videoStream;
        
        detectionActive = true;
        processFrame();
        
        showNotification('Detection started', 'success');
        document.getElementById('detection-status').innerHTML = '<div class="alert alert-success"><i class="fas fa-video"></i> Detection Active</div>';
        
        // Start socket stream
        socket.emit('start_stream', { stream_id: 'webcam' });
        
    } catch (error) {
        console.error('Error starting detection:', error);
        showNotification('Could not access camera', 'danger');
    }
}

// Process frames for detection
async function processFrame() {
    if (!detectionActive) return;
    
    const videoElement = document.getElementById('video-feed');
    if (videoElement.videoWidth > 0) {
        // Capture frame
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        
        // Send for analysis
        const imageData = canvas.toDataURL('image/jpeg');
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageData })
            });
            
            const result = await response.json();
            updateDetectionInfo(result);
            
        } catch (error) {
            console.error('Analysis error:', error);
        }
    }
    
    setTimeout(processFrame, 100);
}

// Update detection information
function updateDetectionInfo(result) {
    document.getElementById('vehicle-count').textContent = result.vehicle_count || 0;
    document.getElementById('confidence').textContent = `${(result.confidence * 100).toFixed(1)}%`;
    
    if (result.accident_detected) {
        document.getElementById('severity').innerHTML = `<span class="badge bg-danger">${result.severity}</span>`;
        document.getElementById('detection-status').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> 
                ACCIDENT DETECTED! Severity: ${result.severity}
            </div>
        `;
    } else {
        document.getElementById('severity').innerHTML = '<span class="badge bg-success">NONE</span>';
        document.getElementById('detection-status').innerHTML = '<div class="alert alert-success"><i class="fas fa-shield-alt"></i> Monitoring...</div>';
    }
}

// Update detection status from socket
function updateDetectionStatus(data) {
    document.getElementById('vehicle-count').textContent = data.vehicle_count || 0;
    if (data.severity) {
        document.getElementById('severity').innerHTML = `<span class="badge bg-danger">${data.severity}</span>`;
        document.getElementById('detection-status').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> 
                ACCIDENT DETECTED! Severity: ${data.severity} (${data.severity_score}%)
            </div>
        `;
    }
}

// Stop detection
function stopDetection() {
    detectionActive = false;
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        document.getElementById('video-feed').srcObject = null;
    }
    showNotification('Detection stopped', 'warning');
    document.getElementById('detection-status').innerHTML = '<div class="alert alert-warning"><i class="fas fa-stop"></i> Detection Stopped</div>';
}

// Capture current frame
function captureFrame() {
    const videoElement = document.getElementById('video-feed');
    if (videoElement.srcObject) {
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoElement, 0, 0);
        
        // Download image
        const link = document.createElement('a');
        link.download = `capture_${new Date().toISOString()}.jpg`;
        link.href = canvas.toDataURL();
        link.click();
        
        showNotification('Frame captured', 'success');
    }
}

// Upload video for processing
async function uploadVideo() {
    const fileInput = document.getElementById('video-upload');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a video file', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('video', file);
    
    document.getElementById('upload-status').innerHTML = '<div class="alert alert-info"><i class="fas fa-spinner fa-spin"></i> Uploading...</div>';
    
    try {
        const response = await fetch('/api/upload_video', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        if (result.success) {
            document.getElementById('upload-status').innerHTML = '<div class="alert alert-success">Uploaded! Processing in background...</div>';
            showNotification('Video uploaded successfully', 'success');
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        document.getElementById('upload-status').innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

// Load vehicles
async function loadVehicles() {
    try {
        const response = await fetch('/api/vehicles');
        const vehicles = await response.json();
        
        const tbody = document.getElementById('vehicles-list');
        if (vehicles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No vehicles registered</td></tr>';
        } else {
            tbody.innerHTML = vehicles.map(vehicle => `
                <tr>
                    <td>${vehicle.license_plate}</td>
                    <td>${vehicle.owner_name}</td>
                    <td>${vehicle.phone}</td>
                    <td>${vehicle.email}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteVehicle('${vehicle.license_plate}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading vehicles:', error);
    }
}

// Add vehicle
async function addVehicle() {
    const vehicle = {
        license_plate: document.getElementById('license-plate').value,
        owner_name: document.getElementById('owner-name').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value,
        vehicle_model: document.getElementById('vehicle-model').value,
        vehicle_color: document.getElementById('vehicle-color').value
    };
    
    try {
        const response = await fetch('/api/vehicles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(vehicle)
        });
        
        const result = await response.json();
        if (result.success) {
            showNotification('Vehicle added successfully', 'success');
            loadVehicles();
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addVehicleModal'));
            modal.hide();
            // Clear form
            document.querySelectorAll('#addVehicleModal input').forEach(input => input.value = '');
        } else {
            showNotification(result.message, 'danger');
        }
    } catch (error) {
        showNotification('Error adding vehicle', 'danger');
    }
}

// Delete vehicle
async function deleteVehicle(licensePlate) {
    if (!confirm(`Are you sure you want to delete vehicle ${licensePlate}?`)) return;
    
    try {
        const response = await fetch(`/api/vehicles?license_plate=${licensePlate}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (result.success) {
            showNotification('Vehicle deleted', 'success');
            loadVehicles();
        } else {
            showNotification(result.message, 'danger');
        }
    } catch (error) {
        showNotification('Error deleting vehicle', 'danger');
    }
}

// Load evidence
async function loadEvidence() {
    try {
        const response = await fetch('/api/accidents?limit=20');
        const accidents = await response.json();
        
        const gallery = document.getElementById('evidence-gallery');
        if (accidents.length === 0) {
            gallery.innerHTML = '<div class="text-center">No evidence captured yet</div>';
        } else {
            gallery.innerHTML = accidents.map(accident => `
                <div class="col-md-4 mb-3">
                    <div class="card evidence-card" onclick="viewEvidence('${accident.accident_id}')">
                        <img src="${accident.evidence_urls?.snapshot || ''}" class="card-img-top" alt="Evidence">
                        <div class="card-body">
                            <h6>${new Date(accident.timestamp).toLocaleString()}</h6>
                            <p>Severity: <span class="badge bg-${accident.severity === 'CRITICAL' ? 'danger' : accident.severity === 'MAJOR' ? 'warning' : 'info'}">${accident.severity}</span></p>
                            <p>Confidence: ${accident.confidence}%</p>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading evidence:', error);
    }
}

// View evidence details
function viewEvidence(accidentId) {
    // Implement evidence viewer modal
    showNotification(`Viewing evidence for accident ${accidentId}`, 'info');
}

// Show accident alert
function showAccidentAlert(data) {
    const toast = new bootstrap.Toast(document.getElementById('alert-toast'));
    const message = document.getElementById('alert-message');
    
    message.innerHTML = `
        <strong>🚨 ACCIDENT DETECTED!</strong><br>
        Severity: ${data.severity}<br>
        Confidence: ${data.confidence}%<br>
        Time: ${new Date().toLocaleString()}
    `;
    
    toast.show();
    
    // Play alert sound
    playAlertSound();
}

// Play alert sound
function playAlertSound() {
    const audio = new Audio('https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3');
    audio.play().catch(e => console.log('Audio play failed:', e));
}

// Show notification
function showNotification(message, type) {
    // Create temporary notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Export report
async function exportReport() {
    try {
        const response = await fetch('/api/export_report');
        const report = await response.json();
        
        // Download JSON file
        const dataStr = JSON.stringify(report, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `accident_report_${new Date().toISOString()}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        showNotification('Report exported successfully', 'success');
    } catch (error) {
        showNotification('Error exporting report', 'danger');
    }
}

// Update severity chart
function updateSeverityChart() {
    const ctx = document.getElementById('severity-chart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Minor', 'Major', 'Critical'],
            datasets: [{
                data: [45, 30, 25],
                backgroundColor: ['#ffc107', '#fd7e14', '#dc3545'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Load alerts
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts?limit=50');
        const alerts = await response.json();
        
        const alertsDiv = document.getElementById('alerts-list');
        if (alerts.length === 0) {
            alertsDiv.innerHTML = '<div class="text-center">No alerts sent</div>';
        } else {
            alertsDiv.innerHTML = alerts.map(alert => `
                <div class="alert alert-${alert.severity === 'CRITICAL' ? 'danger' : alert.severity === 'MAJOR' ? 'warning' : 'info'}">
                    <strong>${new Date(alert.timestamp).toLocaleString()}</strong><br>
                    Vehicle: ${alert.license_plate}<br>
                    Severity: ${alert.severity}<br>
                    Alerts Sent: ${alert.alerts_sent?.length || 0}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initSocket();
    loadDashboardStats();
    loadVehicles();
    loadEvidence();
    loadAlerts();
    updateSeverityChart();
    
    // Refresh stats every 30 seconds
    setInterval(loadDashboardStats, 30000);
    setInterval(loadEvidence, 30000);
    setInterval(loadAlerts, 30000);
});
