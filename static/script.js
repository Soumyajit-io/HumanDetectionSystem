
let streamActive = false;
let detectActive = false;
let statusInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    updateStatus();
    statusInterval = setInterval(updateStatus, 1000);
    updateUI();
});

// Start the camera stream on server
async function startStream() {
    try {
        const res = await fetch('/start_stream', { method: 'POST' });
        const data = await res.json();
        if (data.stream_active) {
            streamActive = true;
            const video = document.getElementById('videoStream');
            const placeholder = document.getElementById('videoPlaceholder');
            video.src = `/camera?t=${Date.now()}`;
            video.style.display = 'block';
            placeholder.style.display = 'none';
            document.getElementById('cameraText').textContent = 'On';
            document.getElementById('cameraStatus').className = 'status-indicator status-online';
            updateUI();
        } else {
            alert('Failed to start stream');
        }
    } catch (err) {
        console.error('startStream error', err);
        alert('Could not start stream (check webcam permissions)');
    }
}

// Stop the camera stream on server
async function stopStream() {
    try {
        const res = await fetch('/stop_stream', { method: 'POST' });
        const data = await res.json();
        if (!data.stream_active) {
            streamActive = false;
            const video = document.getElementById('videoStream');
            const placeholder = document.getElementById('videoPlaceholder');
            video.src = '';
            video.style.display = 'none';
            placeholder.style.display = 'flex';
            document.getElementById('cameraText').textContent = 'Off';
            document.getElementById('cameraStatus').className = 'status-indicator status-offline';
            // also stop detection if running
            detectActive = false;
            updateUI();
        }
    } catch (err) {
        console.error('stopStream error', err);
    }
}

// Toggle detection on server
async function toggleDetect() {
    try {
        const res = await fetch('/toggle_detect', { method: 'POST' });
        const data = await res.json();
        detectActive = data.detect_active;
        updateUI();
    } catch (err) {
        console.error('toggleDetect error', err);
    }
}

// Poll status endpoint and update UI elements
async function updateStatus() {
    try {
        const res = await fetch('/status');
        const data = await res.json();

        // update detection panel
        const alertText = document.getElementById('alertText');
        const lastDetected = document.getElementById('lastDetected');
        const humanCount = document.getElementById('humanCount');
        const detectText = document.getElementById('detectText');
        const detectBar = document.getElementById('detectStatusBar');

        if (data.detected) {
            alertText.textContent = '🚨 Human Detected!';
            lastDetected.textContent = `Last detected: ${data.last_detected_time || '--:--:--'}`;
            humanCount.textContent = `Number of humans: ${data.human_count || 0}`;
            document.getElementById('detectionPanel').classList.remove('safe');
            document.getElementById('detectionPanel').classList.add('detected');

        } else {
            alertText.textContent = '✅ No Human Detected';
            lastDetected.textContent = `Last detected: ${data.last_detected_time || '--:--:--'}`;
            humanCount.textContent = `Number of humans: ${data.human_count || 0}`;
            document.getElementById('detectionPanel').classList.remove('detected');
            document.getElementById('detectionPanel').classList.add('safe');
        }

        // stream & detect status
        streamActive = !!data.stream_active;
        detectActive = !!data.detect_active;

        if (streamActive) {
            document.getElementById('cameraText').textContent = 'On';
            document.getElementById('cameraStatus').className = 'status-indicator status-online';
        } else {
            document.getElementById('cameraText').textContent = 'Off';
            document.getElementById('cameraStatus').className = 'status-indicator status-offline';
        }

        if (detectActive) {
            detectText.textContent = 'Detecting';
            detectBar.className = 'status-indicator status-searching';
            document.getElementById('detectBtn').textContent = 'Stop Detect';
        } else {
            detectText.textContent = 'Idle';
            detectBar.className = 'status-indicator status-offline';
            document.getElementById('detectBtn').textContent = 'Detect Humans';
        }

    } catch (err) {
        console.error('updateStatus error', err);
    }
}

function updateUI() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const detectBtn = document.getElementById('detectBtn');

    startBtn.disabled = streamActive;
    stopBtn.disabled = !streamActive;
    detectBtn.disabled = !streamActive;

    if (detectActive) {
        detectBtn.classList.add('recording');
        detectBtn.textContent = 'Stop Detect';
    } else {
        detectBtn.classList.remove('recording');
        detectBtn.textContent = 'Detect Humans';
    }
}

// dummy functions
function adjustBrightness(v){}
function adjustContrast(v){}
function toggleFullscreen() {
    const videoContainer = document.querySelector('.video-container');
    if (!document.fullscreenElement) {
        videoContainer.requestFullscreen().catch(()=>{});
    } else { document.exitFullscreen(); }
}
function dummyRecord(){ alert('Record is a dummy button in this prototype'); }
