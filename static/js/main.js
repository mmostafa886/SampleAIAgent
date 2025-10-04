/**
 * Test Case Generator - Frontend Logic
 * Handles user interactions and API communication
 */

// State management
let currentTab = 'text';
let uploadedFileContent = '';
let logs = [];

/**
 * Log management functions
 */
function addLog(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = {
        timestamp,
        message,
        type
    };

    logs.push(logEntry);

    const logsContent = document.getElementById('logsContent');
    const logDiv = document.createElement('div');
    logDiv.className = `log-entry ${type}`;
    logDiv.innerHTML = `
        <span class="log-timestamp">[${timestamp}]</span>
        <span class="log-message">${message}</span>
    `;

    logsContent.appendChild(logDiv);
    logsContent.scrollTop = logsContent.scrollHeight;

    // Also log to console
    console.log(`[${type.toUpperCase()}] ${message}`);
}

function clearLogs() {
    logs = [];
    const logsContent = document.getElementById('logsContent');
    logsContent.innerHTML = `
        <div class="log-entry info">
            <span class="log-timestamp">[Cleared]</span>
            <span class="log-message">Logs cleared. Ready for new entries...</span>
        </div>
    `;
    addLog('Logs cleared by user', 'info');
}

function exportLogs() {
    const logText = logs.map(log => `[${log.timestamp}] [${log.type.toUpperCase()}] ${log.message}`).join('\n');
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs_${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    addLog('Logs exported successfully', 'success');
}

function toggleLogs() {
    const panel = document.getElementById('logsPanel');
    panel.classList.toggle('open');

    const button = document.querySelector('.logs-toggle');
    if (panel.classList.contains('open')) {
        button.textContent = '✖️ Close Logs';
    } else {
        button.textContent = '📊 View Logs';
    }
}

/**
 * Switch between text input and file upload tabs
 */
function switchTab(tab) {
    currentTab = tab;

    // Update tab buttons
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    if (tab === 'text') {
        document.getElementById('textTab').classList.add('active');
    } else {
        document.getElementById('fileTab').classList.add('active');
    }
}

/**
 * Handle file selection from file input
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('fileName').textContent = `Selected: ${file.name}`;

        const reader = new FileReader();
        reader.onload = function(e) {
            uploadedFileContent = e.target.result;
        };
        reader.onerror = function() {
            showResult(false, 'Failed to read file. Please try again.');
        };
        reader.readAsText(file);
    }
}

/**
 * Get user story content based on current active tab
 */
function getUserStory() {
    if (currentTab === 'text') {
        return document.getElementById('userStoryText').value.trim();
    } else {
        return uploadedFileContent.trim();
    }
}

/**
 * Validate user inputs
 */
function validateInputs() {
    const userStory = getUserStory();

    if (!userStory) {
        showResult(false, 'Please provide a user story');
        return false;
    }

    return true;
}

/**
 * Show/hide UI elements during processing
 */
function setLoadingState(isLoading) {
    const loader = document.getElementById('loader');
    const resultDiv = document.getElementById('result');
    const generateBtn = document.querySelector('.generate-btn');

    loader.style.display = isLoading ? 'block' : 'none';
    resultDiv.style.display = 'none';
    generateBtn.disabled = isLoading;
    generateBtn.textContent = isLoading ? '⏳ Generating...' : '✨ Generate Test Cases';
}

/**
 * Main function to generate test cases
 */
async function generateTestCases() {
    addLog('='.repeat(50), 'info');
    addLog('🚀 Generate button clicked', 'info');

    // Validate inputs
    if (!validateInputs()) {
        addLog('❌ Validation failed', 'error');
        return;
    }

    const userStory = getUserStory();
    const filename = document.getElementById('filename').value.trim() || 'test_cases';

    addLog(`📝 User story: ${userStory.length} characters`, 'info');
    addLog(`📁 Filename: ${filename}`, 'info');

    // Show loading state
    setLoadingState(true);
    addLog('⏳ Starting generation process...', 'info');

    try {
        addLog('📤 Sending request to server...', 'info');

        const requestBody = {
            user_story: userStory,
            filename: filename
        };

        // Make API request
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        addLog(`📥 Response received (Status: ${response.status})`, 'info');

        const data = await response.json();

        // Handle response
        if (data.success) {
            addLog(`✅ SUCCESS! Generated ${data.count} test cases`, 'success');
            addLog(`📄 Filename: ${data.filename}`, 'success');
            addLog(`📂 Saved to: ${data.filepath}`, 'success');
            showResult(true, data.message, data.filename, data.count, data.filepath);
        } else {
            addLog(`❌ FAILED: ${data.message}`, 'error');
            showResult(false, data.message);
        }

    } catch (error) {
        addLog(`❌ Network error: ${error.message}`, 'error');
        showResult(false, `Network error: ${error.message}`);
    } finally {
        setLoadingState(false);
        addLog('='.repeat(50), 'info');
    }
}

/**
 * Display result message to user
 */
function showResult(success, message, filename = null, count = null, filepath = null) {
    addLog('📺 Displaying result on page', 'info');

    const resultDiv = document.getElementById('result');

    // Make absolutely sure it's visible
    resultDiv.style.display = 'block';
    resultDiv.style.opacity = '1';
    resultDiv.className = 'result ' + (success ? 'success' : 'error');

    if (success) {
        const fullPath = filepath || `generated_test_cases/${filename}`;
        resultDiv.innerHTML = `
            <h3>✅ Success!</h3>
            <p><strong>${count}</strong> test cases have been generated successfully.</p>
            <p><strong>Filename:</strong> ${filename}</p>
            <p><strong>Saved to:</strong> ${fullPath}</p>
            <br>
            <a href="/download/${filename}" class="download-btn" download>
                ⬇️ Download CSV File
            </a>
        `;
        addLog('✅ Success message displayed on page', 'success');
    } else {
        resultDiv.innerHTML = `
            <h3>❌ Error</h3>
            <p><strong>Something went wrong:</strong></p>
            <p>${message}</p>
        `;
        addLog('❌ Error message displayed on page', 'error');
    }

    // Force scroll to result
    setTimeout(() => {
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
}

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    addLog('🧪 Test Case Generator initialized', 'success');
    addLog('Ready to generate test cases!', 'info');

    // Add enter key listener to filename input
    const filenameInput = document.getElementById('filename');
    if (filenameInput) {
        filenameInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                addLog('Enter key pressed - triggering generation', 'info');
                generateTestCases();
            }
        });
    }
});