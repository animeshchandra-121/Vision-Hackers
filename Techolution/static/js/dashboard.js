// Dashboard JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Load dashboard data
    loadDashboardData();
    
    // Update data every 30 seconds
    setInterval(loadDashboardData, 30000);
});

async function loadDashboardData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        // Update stats
        document.getElementById('employee-count').textContent = data.employees_count || 0;
        document.getElementById('project-count').textContent = data.projects_count || 0;
        
        // Calculate match rate (simulated)
        const matchRate = data.employees_loaded && data.projects_loaded ? 
            Math.floor(Math.random() * 20) + 80 : 0;
        document.getElementById('match-rate').textContent = matchRate + '%';
        
        // Calculate average processing time (simulated)
        const avgTime = data.employees_loaded && data.projects_loaded ? 
            (Math.random() * 2 + 1).toFixed(1) : 0;
        document.getElementById('avg-time').textContent = avgTime + 's';
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Add interactive effects to feature items
document.addEventListener('DOMContentLoaded', function() {
    const featureItems = document.querySelectorAll('.feature-item');
    
    featureItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 15px 30px rgba(0,0,0,0.15)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
        });
    });
    
    // Add progress bars to roadmap items
    const roadmapItems = document.querySelectorAll('.roadmap-item');
    roadmapItems.forEach((item, index) => {
        if (index === 0) {
            // Phase 1 is complete
            const progressBar = document.createElement('div');
            progressBar.className = 'progress-bar';
            progressBar.innerHTML = '<div class="progress-fill" style="width: 100%"></div>';
            item.appendChild(progressBar);
        } else if (index === 1) {
            // Phase 2 is in progress
            const progressBar = document.createElement('div');
            progressBar.className = 'progress-bar';
            progressBar.innerHTML = '<div class="progress-fill" style="width: 60%"></div>';
            item.appendChild(progressBar);
        } else {
            // Phase 3 is planned
            const progressBar = document.createElement('div');
            progressBar.className = 'progress-bar';
            progressBar.innerHTML = '<div class="progress-fill" style="width: 0%"></div>';
            item.appendChild(progressBar);
        }
    });
});

// Add CSS for progress bars
const style = document.createElement('style');
style.textContent = `
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e9ecef;
        border-radius: 4px;
        margin-top: 1rem;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
`;
document.head.appendChild(style);
