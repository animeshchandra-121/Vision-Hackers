// Prototype page JavaScript functionality
let uploadedFiles = {
    employees: null,
    projects: null
};

document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    loadDataStatus();
});

function initializeFileUpload() {
    // Employees file upload
    const employeesUpload = document.getElementById('employees-upload');
    const employeesFile = document.getElementById('employees-file');
    
    employeesUpload.addEventListener('click', () => employeesFile.click());
    employeesUpload.addEventListener('dragover', handleDragOver);
    employeesUpload.addEventListener('dragleave', handleDragLeave);
    employeesUpload.addEventListener('drop', (e) => handleDrop(e, 'employees'));
    
    employeesFile.addEventListener('change', (e) => handleFileSelect(e, 'employees'));
    
    // Projects file upload
    const projectsUpload = document.getElementById('projects-upload');
    const projectsFile = document.getElementById('projects-file');
    
    projectsUpload.addEventListener('click', () => projectsFile.click());
    projectsUpload.addEventListener('dragover', handleDragOver);
    projectsUpload.addEventListener('dragleave', handleDragLeave);
    projectsUpload.addEventListener('drop', (e) => handleDrop(e, 'projects'));
    
    projectsFile.addEventListener('change', (e) => handleFileSelect(e, 'projects'));
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e, type) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0], type);
    }
}

function handleFileSelect(e, type) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file, type);
    }
}

function handleFile(file, type) {
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
        alert('Please upload a CSV file');
        return;
    }
    
    uploadedFiles[type] = file;
    
    // Update UI
    const uploadArea = document.getElementById(`${type}-upload`);
    const fileInfo = document.getElementById(`${type}-info`);
    const filename = document.getElementById(`${type}-filename`);
    
    uploadArea.style.display = 'none';
    fileInfo.style.display = 'flex';
    filename.textContent = file.name;
    
    // Update buttons
    updateButtonStates();
    
    // Show preview
    showFilePreview(file, type);
}

function removeFile(type) {
    uploadedFiles[type] = null;
    
    // Update UI
    const uploadArea = document.getElementById(`${type}-upload`);
    const fileInfo = document.getElementById(`${type}-info`);
    const fileInput = document.getElementById(`${type}-file`);
    
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
    fileInput.value = '';
    
    // Update buttons
    updateButtonStates();
    
    // Clear preview
    clearPreview(type);
}

function updateButtonStates() {
    const uploadBtn = document.getElementById('upload-btn');
    const matchBtn = document.getElementById('match-btn');
    
    const hasFiles = uploadedFiles.employees || uploadedFiles.projects;
    uploadBtn.disabled = !hasFiles;
    
    // Check if data is loaded
    checkDataStatus();
}

async function checkDataStatus() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        const matchBtn = document.getElementById('match-btn');
        matchBtn.disabled = !(data.employees_loaded && data.projects_loaded);
    } catch (error) {
        console.error('Error checking data status:', error);
    }
}

function showFilePreview(file, type) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const csv = e.target.result;
        const lines = csv.split('\n');
        const headers = lines[0].split(',');
        const previewData = lines.slice(1, 6); // Show first 5 rows
        
        const previewContainer = document.getElementById(`${type}-preview`);
        let html = '<table><thead><tr>';
        
        headers.forEach(header => {
            html += `<th>${header.trim()}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        previewData.forEach(row => {
            if (row.trim()) {
                html += '<tr>';
                const cells = row.split(',');
                cells.forEach(cell => {
                    html += `<td>${cell.trim()}</td>`;
                });
                html += '</tr>';
            }
        });
        
        html += '</tbody></table>';
        previewContainer.innerHTML = html;
    };
    reader.readAsText(file);
}

function clearPreview(type) {
    const previewContainer = document.getElementById(`${type}-preview`);
    previewContainer.innerHTML = '<p>No data loaded. Upload a file to see preview.</p>';
}

function showPreview(type) {
    // Hide all previews
    document.querySelectorAll('.preview-table').forEach(preview => {
        preview.style.display = 'none';
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected preview
    document.getElementById(`${type}-preview`).style.display = 'block';
    
    // Add active class to selected tab
    event.target.classList.add('active');
}

async function uploadFiles() {
    const formData = new FormData();
    
    if (uploadedFiles.employees) {
        formData.append('employees', uploadedFiles.employees);
    }
    if (uploadedFiles.projects) {
        formData.append('projects', uploadedFiles.projects);
    }
    
    showLoading('Uploading files...', 'Please wait while we process your data');
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Update status
            updateDataStatus();
            
            // Show success message
            showNotification('Files uploaded successfully!', 'success');
            
            // Update button states
            checkDataStatus();
            
        } else {
            showNotification('Error uploading files: ' + result.message, 'error');
        }
    } catch (error) {
        showNotification('Error uploading files: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function performMatching() {
    showLoading('Performing AI matching...', 'Analyzing data and generating optimal allocations');
    
    try {
        const response = await fetch('/api/match', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Redirect to results page
            window.location.href = '/results';
        } else {
            showNotification('Error performing matching: ' + result.message, 'error');
        }
    } catch (error) {
        showNotification('Error performing matching: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function loadDataStatus() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        updateDataStatus(data);
    } catch (error) {
        console.error('Error loading data status:', error);
    }
}

function updateDataStatus(data = null) {
    if (data) {
        document.getElementById('data-status').textContent = 
            data.employees_loaded && data.projects_loaded ? 'Data loaded' : 'No data';
    }
}

function showLoading(text, subtext) {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const loadingSubtext = document.getElementById('loading-subtext');
    
    loadingText.textContent = text;
    loadingSubtext.textContent = subtext;
    overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'none';
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        animation: slideIn 0.3s ease;
    `;
    
    // Add animation keyframes
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}
