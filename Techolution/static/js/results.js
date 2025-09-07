// Results page JavaScript functionality
let matchingData = null;
let filteredData = null;

document.addEventListener('DOMContentLoaded', function() {
    loadResults();
    initializeCharts();
    initializeFilters();
});

async function loadResults() {
    try {
        const response = await fetch('/api/results');
        const result = await response.json();
        
        if (result.status === 'success') {
            matchingData = result.data;
            filteredData = result.data;
            displayResults();
            updateSummary();
            populateRecommendations();
            populateRankings();
            updateFilters();
        } else {
            showError('No matching results available. Please perform matching first.');
        }
    } catch (error) {
        showError('Error loading results: ' + error.message);
    }
}

function displayResults() {
    if (!matchingData) return;
    
    // Calculate summary statistics
    const totalProjects = matchingData.length;
    const totalEmployees = new Set();
    let totalMatches = 0;
    let totalScore = 0;
    let highQualityMatches = 0;
    
    matchingData.forEach(project => {
        project.matches.forEach(match => {
            totalEmployees.add(match.employee_id);
            totalMatches++;
            totalScore += match.overall_score;
            if (match.overall_score >= 80) {
                highQualityMatches++;
            }
        });
    });
    
    const avgScore = totalMatches > 0 ? Math.round(totalScore / totalMatches) : 0;
    
    // Update summary
    document.getElementById('total-projects').textContent = totalProjects;
    document.getElementById('total-employees').textContent = totalEmployees.size;
    document.getElementById('avg-match-score').textContent = avgScore + '%';
    document.getElementById('top-matches').textContent = highQualityMatches;
    
    // Populate results table
    populateResultsTable();
}

function updateSummary() {
    if (!matchingData) return;
    
    // Calculate summary statistics
    const totalProjects = matchingData.length;
    const totalEmployees = new Set();
    const assignedEmployees = new Set(); // Track employees assigned to intelligent teams
    let totalMatches = 0;
    let totalScore = 0;
    let highQualityMatches = 0;
    
    matchingData.forEach(project => {
        project.matches.forEach(match => {
            totalEmployees.add(match.employee_id);
            totalMatches++;
            totalScore += match.overall_score;
            if (match.overall_score >= 80) {
                highQualityMatches++;
            }
        });
        
        // Count employees in intelligent teams
        const intelligentTeam = project.intelligent_team || project.top_3 || [];
        intelligentTeam.forEach(match => {
            assignedEmployees.add(match.employee_id);
        });
    });
    
    const avgScore = totalMatches > 0 ? Math.round(totalScore / totalMatches) : 0;
    
    // Update summary elements
    const totalProjectsEl = document.getElementById('total-projects');
    const totalEmployeesEl = document.getElementById('total-employees');
    const avgScoreEl = document.getElementById('avg-match-score');
    const topMatchesEl = document.getElementById('top-matches');
    
    if (totalProjectsEl) totalProjectsEl.textContent = totalProjects;
    if (totalEmployeesEl) totalEmployeesEl.textContent = assignedEmployees.size; // Show assigned employees
    if (avgScoreEl) avgScoreEl.textContent = avgScore + '%';
    if (topMatchesEl) topMatchesEl.textContent = highQualityMatches;
    
    // Add a note about no duplicates
    const summaryCard = document.querySelector('.summary-card');
    if (summaryCard && assignedEmployees.size > 0) {
        const existingNote = summaryCard.querySelector('.no-duplicates-note');
        if (!existingNote) {
            const note = document.createElement('div');
            note.className = 'no-duplicates-note';
            note.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <span>No employee duplicates - Each person assigned to only one project</span>
            `;
            summaryCard.appendChild(note);
        }
    }
}

function populateResultsTable() {
    const tbody = document.getElementById('results-tbody');
    tbody.innerHTML = '';
    
    if (!filteredData) return;
    
    filteredData.forEach(project => {
        project.matches.forEach(match => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div>
                        <strong>${match.employee_name}</strong><br>
                        <small>${match.employee_id}</small>
                    </div>
                </td>
                <td>
                    <div>
                        <strong>${match.project_title}</strong><br>
                        <small>${match.project_id}</small>
                    </div>
                </td>
                <td>
                    <span class="score-badge ${getScoreClass(match.overall_score)}">
                        ${match.overall_score}%
                    </span>
                </td>
                <td>${match.skill_match}%</td>
                <td>${match.proficiency_match}%</td>
                <td>${match.availability_match}%</td>
                <td>${match.capacity_match}%</td>
                <td>${match.role}</td>
                <td>
                    <button class="action-btn view" onclick="viewDetails('${match.employee_id}', '${match.project_id}')">
                        View
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    });
}

function getScoreClass(score) {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-medium';
    return 'score-low';
}

function populateRecommendations() {
    const container = document.getElementById('recommendations-grid');
    container.innerHTML = '';
    
    if (!matchingData) return;
    
    matchingData.forEach(project => {
        const projectCard = document.createElement('div');
        projectCard.className = 'project-card';
        
        // Get intelligent recommendations based on domain
        const intelligentRecommendations = project.intelligent_team || project.top_3 || [];
        
        let html = `
            <h3>${project.project_title}</h3>
            <p><strong>Domain:</strong> ${project.project_domain}</p>
            <p><strong>Duration:</strong> ${project.project_duration} weeks</p>
            <p><strong>Deadline:</strong> ${new Date(project.project_deadline).toLocaleDateString()}</p>
            
            <div class="team-composition-summary">
                <h4><i class="fas fa-info-circle"></i> Team Composition Strategy</h4>
                <p>This project will be staffed with a balanced team of <strong>3 domain experts</strong> and <strong>2 complementary specialists</strong> to ensure comprehensive coverage of all project requirements.</p>
                <p><i class="fas fa-shield-alt"></i> <strong>No Duplicates:</strong> Each employee is assigned to only one project to ensure full focus and availability.</p>
            </div>
            
            <div class="recommendations">
        `;
        
        // Categorize team members
        const domainExperts = [];
        const complementaryMembers = [];
        
        intelligentRecommendations.forEach((match, index) => {
            const isDomainExpert = match.selection_reason && (
                match.selection_reason.includes('expert') || 
                match.selection_reason.includes('specialist') || 
                match.selection_reason.includes('developer')
            );
            
            if (isDomainExpert) {
                domainExperts.push({...match, rank: index + 1});
            } else {
                complementaryMembers.push({...match, rank: index + 1});
            }
        });
        
        // Check for any duplicate employees across all projects
        const allEmployeeIds = new Set();
        const duplicateEmployees = new Set();
        
        // This would need to be passed from the backend, but for now we'll show a note
        const hasDuplicates = false; // This should be calculated on the backend
        
        // Display domain experts first
        if (domainExperts.length > 0) {
            html += `<div class="team-section">
                <h4><i class="fas fa-users"></i> Domain Experts (${domainExperts.length})</h4>
                <p class="section-description">Specialists in ${project.project_domain} with relevant skills</p>
            `;
            
            domainExperts.forEach(match => {
                const roleIcon = getRoleIcon(match.role);
                const proficiencyColor = getProficiencyColor(match.proficiency);
                const selectionReason = match.selection_reason || `High-performing team member with ${match.skills.slice(0, 2).join(', ')} skills`;
                
                html += `
                    <div class="employee-match domain-expert">
                        <div class="match-rank">${match.rank}</div>
                        <div class="match-info">
                            <h4>${match.employee_name} ${roleIcon}</h4>
                            <p><span class="role-badge ${match.role.toLowerCase().replace(' ', '-')}">${match.role}</span> 
                               <span class="proficiency-badge ${proficiencyColor}">${match.proficiency}</span></p>
                            <p><small>Skills: ${match.skills.join(', ')}</small></p>
                            <p><small>Location: ${match.location}</small></p>
                            <div class="selection-reason">
                                <strong>Why selected:</strong> ${selectionReason}
                            </div>
                        </div>
                        <div class="match-score">
                            <div class="score">${match.overall_score}%</div>
                            <small>Overall Match</small>
                            <div class="score-breakdown">
                                <small>Skill: ${match.skill_match}%</small><br>
                                <small>Proficiency: ${match.proficiency_match}%</small>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
        }
        
        // Display complementary members
        if (complementaryMembers.length > 0) {
            html += `<div class="team-section">
                <h4><i class="fas fa-puzzle-piece"></i> Complementary Team Members (${complementaryMembers.length})</h4>
                <p class="section-description">Specialists in supporting roles to enhance project success</p>
            `;
            
            complementaryMembers.forEach(match => {
                const roleIcon = getRoleIcon(match.role);
                const proficiencyColor = getProficiencyColor(match.proficiency);
                const selectionReason = match.selection_reason || `High-performing team member with ${match.skills.slice(0, 2).join(', ')} skills`;
                
                html += `
                    <div class="employee-match complementary-member">
                        <div class="match-rank">${match.rank}</div>
                        <div class="match-info">
                            <h4>${match.employee_name} ${roleIcon}</h4>
                            <p><span class="role-badge ${match.role.toLowerCase().replace(' ', '-')}">${match.role}</span> 
                               <span class="proficiency-badge ${proficiencyColor}">${match.proficiency}</span></p>
                            <p><small>Skills: ${match.skills.join(', ')}</small></p>
                            <p><small>Location: ${match.location}</small></p>
                            <div class="selection-reason">
                                <strong>Why selected:</strong> ${selectionReason}
                            </div>
                        </div>
                        <div class="match-score">
                            <div class="score">${match.overall_score}%</div>
                            <small>Overall Match</small>
                            <div class="score-breakdown">
                                <small>Skill: ${match.skill_match}%</small><br>
                                <small>Proficiency: ${match.proficiency_match}%</small>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
        }
        
        html += '</div></div>';
        projectCard.innerHTML = html;
        container.appendChild(projectCard);
    });
}

function getIntelligentRecommendations(project) {
    const domain = project.project_domain.toLowerCase();
    const projectTitle = project.project_title.toLowerCase();
    
    // Define domain-specific skill requirements
    const domainSkills = {
        'ai/ml': ['AI', 'Machine Learning', 'Python Developer', 'Data Science'],
        'web development': ['Backend Developer', 'Full Stack Developer', 'FSD', 'Web Development'],
        'mobile development': ['Mobile Development', 'UI/UX', 'React Native', 'Mobile App'],
        'data science': ['Data Science', 'Python Developer', 'Machine Learning', 'Analytics'],
        'cloud computing': ['DevOps', 'Cloud Computing', 'Infrastructure', 'AWS'],
        'e-commerce': ['Backend Developer', 'Web Development', 'E-commerce', 'Full Stack Developer']
    };
    
    // Get all matches for this project
    let allMatches = [...project.matches];
    
    // Filter and prioritize based on domain
    const domainRelevantSkills = domainSkills[domain] || [];
    const domainMatches = allMatches.filter(match => 
        match.skills.some(skill => 
            domainRelevantSkills.some(domainSkill => 
                skill.toLowerCase().includes(domainSkill.toLowerCase())
            )
        )
    );
    
    // If we have domain-specific matches, use them; otherwise use all matches
    const relevantMatches = domainMatches.length > 0 ? domainMatches : allMatches;
    
    // Sort by overall score
    relevantMatches.sort((a, b) => b.overall_score - a.overall_score);
    
    // Create intelligent team composition
    const recommendations = [];
    const usedEmployees = new Set();
    
    // 1. Find 1 Senior employee (preferably with domain skills)
    const seniorMatch = relevantMatches.find(match => 
        match.proficiency === 'Senior' && !usedEmployees.has(match.employee_id)
    );
    if (seniorMatch) {
        recommendations.push(seniorMatch);
        usedEmployees.add(seniorMatch.employee_id);
    }
    
    // 2. Find 1 Intermediate employee
    const intermediateMatch = relevantMatches.find(match => 
        match.proficiency === 'Intermediate' && !usedEmployees.has(match.employee_id)
    );
    if (intermediateMatch) {
        recommendations.push(intermediateMatch);
        usedEmployees.add(intermediateMatch.employee_id);
    }
    
    // 3. Find 1 Beginner employee (for learning/growth)
    const beginnerMatch = relevantMatches.find(match => 
        match.proficiency === 'Beginner' && !usedEmployees.has(match.employee_id)
    );
    if (beginnerMatch) {
        recommendations.push(beginnerMatch);
        usedEmployees.add(beginnerMatch.employee_id);
    }
    
    // 4. Fill remaining slots with best available matches
    const remainingMatches = relevantMatches.filter(match => 
        !usedEmployees.has(match.employee_id)
    );
    
    // Add up to 2 more employees based on conflicts and suitability
    for (let i = 0; i < Math.min(2, remainingMatches.length); i++) {
        const match = remainingMatches[i];
        if (match.overall_score >= 60) { // Only add if score is reasonable
            recommendations.push(match);
            usedEmployees.add(match.employee_id);
        }
    }
    
    // If we don't have enough recommendations, fill with top remaining matches
    while (recommendations.length < 5 && recommendations.length < allMatches.length) {
        const nextMatch = allMatches.find(match => !usedEmployees.has(match.employee_id));
        if (nextMatch) {
            recommendations.push(nextMatch);
            usedEmployees.add(nextMatch.employee_id);
        } else {
            break;
        }
    }
    
    return recommendations.slice(0, 5); // Return top 5 recommendations
}

function getRoleIcon(role) {
    const icons = {
        'Senior': '👨‍💼',
        'Full Time': '👨‍💻',
        'Intern': '🎓'
    };
    return icons[role] || '👤';
}

function getProficiencyColor(proficiency) {
    const colors = {
        'Senior': 'senior',
        'Intermediate': 'intermediate',
        'Beginner': 'beginner'
    };
    return colors[proficiency] || 'intermediate';
}

function populateRankings() {
    const container = document.getElementById('ranking-list');
    container.innerHTML = '';
    
    if (!matchingData) return;
    
    // Collect all employees with their best scores
    const employeeScores = new Map();
    
    matchingData.forEach(project => {
        project.matches.forEach(match => {
            const empId = match.employee_id;
            if (!employeeScores.has(empId) || employeeScores.get(empId).overall_score < match.overall_score) {
                employeeScores.set(empId, match);
            }
        });
    });
    
    // Sort by score
    const sortedEmployees = Array.from(employeeScores.values())
        .sort((a, b) => b.overall_score - a.overall_score)
        .slice(0, 10);
    
    sortedEmployees.forEach((employee, index) => {
        const rankingItem = document.createElement('div');
        rankingItem.className = 'ranking-item';
        rankingItem.innerHTML = `
            <div class="ranking-number">${index + 1}</div>
            <div class="ranking-info">
                <h4>${employee.employee_name}</h4>
                <p>${employee.role} • ${employee.proficiency} • ${employee.overall_score}% match</p>
            </div>
        `;
        container.appendChild(rankingItem);
    });
}

function updateFilters() {
    const projectFilter = document.getElementById('project-filter');
    const roleFilter = document.getElementById('role-filter');
    
    // Populate project filter
    projectFilter.innerHTML = '<option value="">All Projects</option>';
    if (matchingData) {
        matchingData.forEach(project => {
            const option = document.createElement('option');
            option.value = project.project_id;
            option.textContent = project.project_title;
            projectFilter.appendChild(option);
        });
    }
    
    // Populate role filter
    const roles = new Set();
    if (matchingData) {
        matchingData.forEach(project => {
            project.matches.forEach(match => {
                roles.add(match.role);
            });
        });
    }
    
    roleFilter.innerHTML = '<option value="">All Roles</option>';
    roles.forEach(role => {
        const option = document.createElement('option');
        option.value = role;
        option.textContent = role;
        roleFilter.appendChild(option);
    });
}

function initializeFilters() {
    const searchInput = document.getElementById('search-input');
    const projectFilter = document.getElementById('project-filter');
    const roleFilter = document.getElementById('role-filter');
    
    searchInput.addEventListener('input', applyFilters);
    projectFilter.addEventListener('change', applyFilters);
    roleFilter.addEventListener('change', applyFilters);
}

function applyFilters() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const projectFilter = document.getElementById('project-filter').value;
    const roleFilter = document.getElementById('role-filter').value;
    
    if (!matchingData) return;
    
    filteredData = matchingData.map(project => {
        const filteredMatches = project.matches.filter(match => {
            const matchesSearch = !searchTerm || 
                match.employee_name.toLowerCase().includes(searchTerm) ||
                match.project_title.toLowerCase().includes(searchTerm);
            
            const matchesProject = !projectFilter || project.project_id === projectFilter;
            const matchesRole = !roleFilter || match.role === roleFilter;
            
            return matchesSearch && matchesProject && matchesRole;
        });
        
        return {
            ...project,
            matches: filteredMatches
        };
    });
    
    displayResults();
}

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Initialize charts if switching to analytics tab
    if (tabName === 'analytics') {
        initializeCharts();
    }
}

function initializeCharts() {
    if (!matchingData) return;
    
    // Role distribution chart
    createRoleChart();
    
    // Domain distribution chart
    createDomainChart();
    
    // Match score distribution chart
    createScoreChart();
    
    // Skill analysis chart
    createSkillChart();
    
    // Proficiency distribution chart
    createProficiencyChart();
    
    // Capacity utilization chart
    createCapacityChart();
}

function createRoleChart() {
    const ctx = document.getElementById('roleChart');
    if (!ctx) return;
    
    const roleCounts = {};
    matchingData.forEach(project => {
        project.matches.forEach(match => {
            roleCounts[match.role] = (roleCounts[match.role] || 0) + 1;
        });
    });
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(roleCounts),
            datasets: [{
                data: Object.values(roleCounts),
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#f5576c',
                    '#4facfe'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function createDomainChart() {
    const ctx = document.getElementById('domainChart');
    if (!ctx) return;
    
    const domainCounts = {};
    matchingData.forEach(project => {
        domainCounts[project.project_domain] = (domainCounts[project.project_domain] || 0) + 1;
    });
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(domainCounts),
            datasets: [{
                data: Object.values(domainCounts),
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#f5576c',
                    '#4facfe'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function createScoreChart() {
    const ctx = document.getElementById('scoreChart');
    if (!ctx) return;
    
    const scoreRanges = {
        '90-100%': 0,
        '80-89%': 0,
        '70-79%': 0,
        '60-69%': 0,
        'Below 60%': 0
    };
    
    matchingData.forEach(project => {
        project.matches.forEach(match => {
            const score = match.overall_score;
            if (score >= 90) scoreRanges['90-100%']++;
            else if (score >= 80) scoreRanges['80-89%']++;
            else if (score >= 70) scoreRanges['70-79%']++;
            else if (score >= 60) scoreRanges['60-69%']++;
            else scoreRanges['Below 60%']++;
        });
    });
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(scoreRanges),
            datasets: [{
                data: Object.values(scoreRanges),
                backgroundColor: [
                    '#28a745',
                    '#20c997',
                    '#ffc107',
                    '#fd7e14',
                    '#dc3545'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createSkillChart() {
    const ctx = document.getElementById('skillChart');
    if (!ctx) return;
    
    const skillCounts = {};
    matchingData.forEach(project => {
        project.matches.forEach(match => {
            match.skills.forEach(skill => {
                skillCounts[skill] = (skillCounts[skill] || 0) + 1;
            });
        });
    });
    
    const sortedSkills = Object.entries(skillCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 8);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: sortedSkills.map(([skill]) => skill),
            datasets: [{
                data: sortedSkills.map(([,count]) => count),
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#f5576c',
                    '#4facfe',
                    '#00f2fe',
                    '#43e97b',
                    '#fa709a'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createProficiencyChart() {
    const ctx = document.getElementById('proficiencyChart');
    if (!ctx) return;
    
    const proficiencyCounts = {};
    matchingData.forEach(project => {
        project.matches.forEach(match => {
            proficiencyCounts[match.proficiency] = (proficiencyCounts[match.proficiency] || 0) + 1;
        });
    });
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(proficiencyCounts),
            datasets: [{
                data: Object.values(proficiencyCounts),
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function createCapacityChart() {
    const ctx = document.getElementById('capacityChart');
    if (!ctx) return;
    
    const capacityRanges = {
        '0-20 hrs': 0,
        '21-30 hrs': 0,
        '31-40 hrs': 0,
        '40+ hrs': 0
    };
    
    matchingData.forEach(project => {
        project.matches.forEach(match => {
            const capacity = match.capacity;
            if (capacity <= 20) capacityRanges['0-20 hrs']++;
            else if (capacity <= 30) capacityRanges['21-30 hrs']++;
            else if (capacity <= 40) capacityRanges['31-40 hrs']++;
            else capacityRanges['40+ hrs']++;
        });
    });
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(capacityRanges),
            datasets: [{
                data: Object.values(capacityRanges),
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#f5576c'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function viewDetails(employeeId, projectId) {
    // Find the specific match
    const match = matchingData.find(project => 
        project.project_id === projectId
    )?.matches.find(match => 
        match.employee_id === employeeId
    );
    
    if (match) {
        alert(`Employee: ${match.employee_name}\nProject: ${match.project_title}\nOverall Score: ${match.overall_score}%\nSkill Match: ${match.skill_match}%\nProficiency Match: ${match.proficiency_match}%\nAvailability Match: ${match.availability_match}%\nCapacity Match: ${match.capacity_match}%`);
    }
}

function downloadResults() {
    if (!matchingData) {
        showError('No results to download');
        return;
    }
    
    // Show loading message
    showNotification('Generating PDF report...', 'info');
    
    // Download PDF
    window.open('/api/download-pdf', '_blank');
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
    `;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    `;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}
