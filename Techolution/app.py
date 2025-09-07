from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, flash
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import json
import os
from datetime import datetime, timedelta
import warnings
import hashlib
import secrets
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib.pyplot as plt
import io
import base64
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'datasets'
app.secret_key = 'your-secret-key-change-this-in-production'


# Simple user storage (in production, use a proper database)
users_db = {}

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session

def get_current_user():
    """Get current logged in user"""
    if is_logged_in():
        return users_db.get(session['user_id'])
    return None


def get_chatbot_response(message, page_url='/'):
    """Generate chatbot response based on message and current page"""
    lower_message = message.lower()
    
    # Home page responses
    if page_url == '/' or 'index' in page_url:
        if 'get started' in lower_message or 'start' in lower_message:
            return """To get started with our AI Talent Management System:
            
1. Click the "Get Started" button to create an account
2. Sign up with your email and password
3. Go to the Dashboard to explore features
4. Upload your employee and project data
5. Run the AI matching algorithm
6. View detailed results and analytics

Would you like me to guide you through any specific step?"""
        
        if 'matching' in lower_message or 'how does' in lower_message:
            return """Our AI matching system works through these steps:
            
1. **Skill Analysis**: Uses TF-IDF and cosine similarity to match skills
2. **Proficiency Matching**: Aligns experience levels with project requirements
3. **Availability Check**: Considers timing and capacity constraints
4. **Domain Optimization**: Applies domain-specific bonuses for better matches
5. **Conflict Resolution**: Automatically handles resource conflicts

The system provides a weighted score based on these factors to find the best matches."""
        
        if 'upload' in lower_message or 'data' in lower_message:
            return """To upload your data:
            
1. Go to the Prototype page after logging in
2. Prepare two CSV files:
   - **Employees.csv**: Employee data with skills, roles, availability
   - **Projects.csv**: Project data with requirements and constraints
3. Drag and drop or browse to upload files
4. Preview your data to ensure it's correct
5. Click "Upload Files" to process the data
6. Run the matching algorithm

Need help with the data format? I can provide detailed column requirements."""
    
    # Dashboard responses
    if 'dashboard' in page_url:
        if 'upload' in lower_message or 'data' in lower_message:
            return """To upload data from the dashboard:
            
1. Click "Launch Prototype" button
2. You'll be taken to the upload interface
3. Upload your Employees.csv and Projects.csv files
4. The system will automatically process and validate your data
5. Return to view real-time statistics on the dashboard

The dashboard will show updated counts and status once data is uploaded."""
        
        if 'matching' in lower_message or 'run' in lower_message:
            return """To perform AI matching:
            
1. First, upload your data using the "Launch Prototype" button
2. Go to the Prototype page
3. Click the "MATCH" button to run the AI algorithm
4. The system will analyze all combinations and generate optimal matches
5. View results on the Results page with detailed analytics

The matching process typically takes 1-3 seconds depending on data size."""
        
        if 'results' in lower_message or 'view' in lower_message:
            return """To view your matching results:
            
1. After running the matching algorithm, go to the Results page
2. Explore different tabs:
   - **Overview**: Charts and employee rankings
   - **Recommendations**: Top 3 matches per project
   - **Analytics**: Skill analysis and distributions
   - **Details**: Complete matching table with filtering
3. Download detailed PDF reports with all analytics

The results include intelligent team recommendations with explanations."""
    
    # General responses
    if 'help' in lower_message or 'support' in lower_message:
        return """I'm here to help! I can assist you with:
        
• Getting started with the platform
• Understanding the AI matching process
• Uploading and formatting data
• Interpreting results and analytics
• Navigating the dashboard and features
• Troubleshooting common issues

What specific area would you like help with?"""
    
    if 'features' in lower_message or 'what can' in lower_message:
        return """Our AI Talent Management System offers:
        
🤖 **Intelligent Matching**: AI-powered employee-project matching
📊 **Real-time Analytics**: Interactive charts and visualizations
💬 **Conversational Interface**: Natural language interactions
🛡️ **Conflict Resolution**: Automatic conflict detection and resolution
👁️ **Transparency**: Explainable AI decisions and audit trails
🔄 **Dynamic Adaptation**: Real-time re-planning capabilities

Would you like to know more about any specific feature?"""
    
    if 'contact' in lower_message or 'support' in lower_message:
        return """For additional support:
        
📧 Email: info@aitalentmanager.com
📞 Phone: +1 (555) 123-4567
💬 Use this chatbot for immediate assistance
📖 Check the documentation and help guides

I'm available 24/7 to help you with any questions!"""
    
    # Default response
    return f"""I understand you're asking about "{message}". Let me help you with that!
    
Could you be more specific about what you need help with? I can assist with:
• Getting started
• Data upload process
• Understanding matching results
• Using the dashboard features
• Troubleshooting issues

Just let me know what you'd like to know more about!"""

# Global variables to store data
employees_df = None
projects_df = None
matching_results = None
used_employees_global = set()  # Track globally used employees

def load_data():
    """Load and preprocess the datasets"""
    global employees_df, projects_df
    
    try:
        # Check if CSV files exist, if not try to convert from Excel or create sample data
        employees_csv_exists = os.path.exists('datasets/Employees.csv')
        projects_csv_exists = os.path.exists('datasets/Projects.csv')
        
        # Load employees data
        if employees_csv_exists:
            employees_df = pd.read_csv('datasets/Employees.csv')
        elif os.path.exists('datasets/Employees.csv.xlsx'):
            # Convert Excel to CSV
            try:
                employees_df = pd.read_excel('datasets/Employees.csv.xlsx')
                employees_df.to_csv('datasets/Employees.csv', index=False)
                print("Converted Employees.xlsx to CSV")
            except Exception as e:
                print(f"Error converting Excel file: {e}")
                employees_df = create_sample_employees_data()
        else:
            employees_df = create_sample_employees_data()
        
        # Load projects data
        if projects_csv_exists:
            projects_df = pd.read_csv('datasets/Projects.csv')
        elif os.path.exists('datasets/Projects.csv.xlsx'):
            # Convert Excel to CSV
            try:
                projects_df = pd.read_excel('datasets/Projects.csv.xlsx')
                projects_df.to_csv('datasets/Projects.csv', index=False)
                print("Converted Projects.xlsx to CSV")
            except Exception as e:
                print(f"Error converting Excel file: {e}")
                projects_df = create_sample_projects_data()
        else:
            projects_df = create_sample_projects_data()
        
        # Data preprocessing
        preprocess_data()
        
    except Exception as e:
        print(f"Error loading data: {e}")
        # Create default empty dataframes
        employees_df = pd.DataFrame()
        projects_df = pd.DataFrame()

# def create_sample_employees_data():
#     """Create sample employees data"""
#     return pd.DataFrame({
#         'Emp ID': ['E001', 'E002', 'E003', 'E004', 'E005', 'E006', 'E007', 'E008', 'E009', 'E010'],
#         'Name': ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'David Brown', 
#                 'Emily Davis', 'Chris Lee', 'Lisa Garcia', 'Alex Chen', 'Maria Rodriguez'],
#         'Skills': ['Backend Developer,Python Developer', 'AI,Python Developer', 'UI/UX,FSD', 
#                   'Project Manager', 'Backend Developer,AI', 'Data Science,Python Developer',
#                   'Full Stack Developer,React', 'DevOps,Cloud Computing', 'Mobile Development,React Native',
#                   'Machine Learning,Python Developer'],
#         'Role': ['Senior', 'Full Time', 'Intern', 'Senior', 'Full Time', 'Full Time', 'Intern', 'Senior', 'Full Time', 'Senior'],
#         'Capacity per week (hrs)': [40, 35, 20, 40, 35, 40, 25, 40, 35, 40],
#         'Previous Project Description': ['E-commerce platform', 'ML model development', 'Mobile app design', 
#                                        'Team management', 'Data analysis', 'Big data processing',
#                                        'Web application', 'Infrastructure setup', 'Mobile app development',
#                                        'AI model training'],
#         'Proficiency': ['Senior', 'Intermediate', 'Beginner', 'Senior', 'Intermediate', 'Senior', 
#                        'Beginner', 'Senior', 'Intermediate', 'Senior'],
#         'Available Date': ['2024-01-01', '2024-01-15', '2024-02-01', '2024-01-01', '2024-01-10',
#                           '2024-01-05', '2024-02-15', '2024-01-01', '2024-01-20', '2024-01-01'],
#         'Location': ['India', 'India', 'India', 'India', 'India', 'USA', 'India', 'India', 'India', 'India']
#     })

# def create_sample_projects_data():
#     """Create sample projects data"""
#     return pd.DataFrame({
#         'ID': ['P001', 'P002', 'P003', 'P004', 'P005'],
#         'Project_Title': ['AI Chatbot Development', 'E-commerce Platform', 'Mobile App Design', 
#                          'Data Analytics Dashboard', 'Cloud Migration Project'],
#         'Domain': ['AI/ML', 'Web Development', 'Mobile Development', 'Data Science', 'Cloud Computing'],
#         'Eligibility': ['Senior,Intermediate', 'All', 'Intern,Full Time', 'Senior,Intermediate', 'Senior,Full Time'],
#         'Duration': [12, 8, 6, 10, 16],
#         'Proficiency': ['Senior', 'Intermediate', 'Beginner', 'Senior', 'Senior'],
#         'Conflicts': ['None', 'P001', 'None', 'P002', 'None'],
#         'Hard_Deadline': ['2024-06-01', '2024-04-15', '2024-03-30', '2024-05-20', '2024-07-10'],
#         'Experience_years': [3, 2, 1, 4, 5]
#     })

def preprocess_data():
    """Preprocess the data for analysis"""
    global employees_df, projects_df
    
    if employees_df is not None and not employees_df.empty:
        # Convert date columns
        if 'Available Date' in employees_df.columns:
            employees_df['Available Date'] = pd.to_datetime(employees_df['Available Date'], errors='coerce')
        
        # Create skill vectors
        if 'Skills' in employees_df.columns:
            employees_df['Skills_List'] = employees_df['Skills'].str.split(',').apply(lambda x: [s.strip() for s in x] if pd.notna(x) else [])
    
    if projects_df is not None and not projects_df.empty:
        # Convert date columns
        if 'Hard_Deadline' in projects_df.columns:
            projects_df['Hard_Deadline'] = pd.to_datetime(projects_df['Hard_Deadline'], errors='coerce')
        
        # Create domain vectors
        if 'Domain' in projects_df.columns:
            projects_df['Domain_List'] = projects_df['Domain'].str.split(',').apply(lambda x: [s.strip() for s in x] if pd.notna(x) else [])

def calculate_skill_match(employee_skills, project_requirements):
    """Calculate skill match score between employee and project"""
    if not employee_skills or not project_requirements or pd.isna(project_requirements):
        return 0
    
    # Convert to sets for easier comparison, handling different data types
    if isinstance(employee_skills, list):
        emp_skills = set(str(skill).strip() for skill in employee_skills if skill and str(skill).strip())
    else:
        emp_skills = set(str(employee_skills).split(','))
        emp_skills = set(skill.strip() for skill in emp_skills if skill.strip())
    
    if isinstance(project_requirements, list):
        proj_req = set(str(req).strip() for req in project_requirements if req and str(req).strip())
    else:
        proj_req = set(str(project_requirements).split(','))
        proj_req = set(req.strip() for req in proj_req if req.strip())
    
    # Domain-specific skill mapping for better matching
    domain_skill_mapping = {
        'ai/ml': ['AI', 'Machine Learning', 'Python Developer', 'Data Science', 'ML'],
        'web development': ['Backend Developer', 'Full Stack Developer', 'FSD', 'Web Development', 'Frontend'],
        'mobile development': ['Mobile Development', 'UI/UX', 'React Native', 'Mobile App', 'iOS', 'Android'],
        'data science': ['Data Science', 'Python Developer', 'Machine Learning', 'Analytics', 'Big Data'],
        'cloud computing': ['DevOps', 'Cloud Computing', 'Infrastructure', 'AWS', 'Azure'],
        'e-commerce': ['Backend Developer', 'Web Development', 'E-commerce', 'Full Stack Developer']
    }
    
    # Calculate base Jaccard similarity
    intersection = len(emp_skills.intersection(proj_req))
    union = len(emp_skills.union(proj_req))
    base_score = intersection / union if union > 0 else 0
    
    # Apply domain-specific bonus
    domain_bonus = 0
    project_req_str = str(project_requirements).lower()
    for domain, skills in domain_skill_mapping.items():
        if any(skill.lower() in project_req_str for skill in skills):
            domain_skills = set(skill.lower() for skill in skills)
            emp_skills_lower = set(skill.lower() for skill in emp_skills)
            domain_intersection = len(emp_skills_lower.intersection(domain_skills))
            if domain_intersection > 0:
                domain_bonus = min(0.3, domain_intersection * 0.1)  # Max 30% bonus
                break
    
    return min(1.0, base_score + domain_bonus)

def calculate_proficiency_match(emp_proficiency, proj_proficiency):
    """Calculate proficiency match score"""
    proficiency_levels = {'Beginner': 1, 'Intermediate': 2, 'Senior': 3}
    
    emp_level = proficiency_levels.get(emp_proficiency, 1)
    proj_level = proficiency_levels.get(proj_proficiency, 1)
    
    # Perfect match gets 1.0, higher employee level gets bonus
    if emp_level >= proj_level:
        return 1.0 + (emp_level - proj_level) * 0.1
    else:
        return max(0.1, emp_level / proj_level)

def calculate_availability_score(emp_available_date, project_start_date):
    """Calculate availability score based on timing"""
    if pd.isna(emp_available_date) or pd.isna(project_start_date):
        return 0.5  # Neutral score if dates are missing
    
    if emp_available_date <= project_start_date:
        return 1.0  # Available on time
    else:
        # Penalty for late availability
        days_late = (emp_available_date - project_start_date).days
        return max(0.1, 1.0 - (days_late / 30))  # 30 days penalty period

def calculate_capacity_score(emp_capacity, required_capacity=40):
    """Calculate capacity utilization score"""
    if pd.isna(emp_capacity):
        return 0.5
    
    utilization = min(1.0, emp_capacity / required_capacity) 
    return utilization

def perform_matching():
    """Perform intelligent matching between employees and projects"""
    global employees_df, projects_df, matching_results, used_employees_global
    
    if employees_df is None or projects_df is None or employees_df.empty or projects_df.empty:
        return {"error": "No data available for matching"}
    
    # Reset global used employees for new matching session
    used_employees_global.clear()
    
    results = []
    
    for _, project in projects_df.iterrows():
        project_id = project.get('ID', f"Project_{project.name}")
        project_title = project.get('Project_Title', 'Unknown Project')
        project_domain = project.get('Domain', '')
        project_proficiency = project.get('Proficiency', 'Intermediate')
        project_duration = project.get('Duration', 12)
        project_deadline = project.get('Hard_Deadline', datetime.now() + timedelta(days=30))
        project_conflicts = project.get('Conflicts', 'None')
        
        project_matches = []
        
        for _, employee in employees_df.iterrows():
            try:
                emp_id = employee.get('Emp ID', f"Emp_{employee.name}")
                emp_name = employee.get('Name', 'Unknown')
                
                # Handle skills safely
                emp_skills_raw = employee.get('Skills_List', [])
                if not emp_skills_raw:
                    emp_skills_raw = employee.get('Skills', '')
                    if emp_skills_raw and not pd.isna(emp_skills_raw):
                        emp_skills = [skill.strip() for skill in str(emp_skills_raw).split(',') if skill.strip()]
                    else:
                        emp_skills = []
                else:
                    emp_skills = [str(skill).strip() for skill in emp_skills_raw if skill and str(skill).strip()]
                
                emp_proficiency = employee.get('Proficiency', 'Intermediate')
                emp_capacity = employee.get('Capacity per week (hrs)', 40)
                emp_available = employee.get('Available Date', datetime.now())
                
                # Ensure capacity is numeric
                try:
                    emp_capacity = float(emp_capacity) if not pd.isna(emp_capacity) else 40
                except (ValueError, TypeError):
                    emp_capacity = 40
                
                # Calculate various match scores with error handling
                skill_score = calculate_skill_match(emp_skills, project_domain)
                proficiency_score = calculate_proficiency_match(emp_proficiency, project_proficiency)
                availability_score = calculate_availability_score(emp_available, project_deadline)
                capacity_score = calculate_capacity_score(emp_capacity)
                
                # Apply domain-specific bonus
                domain_bonus = calculate_domain_bonus(emp_skills, project_domain)
                
                # Apply conflict penalty
                conflict_penalty = calculate_conflict_penalty(emp_id, project_conflicts)
                
                # Weighted overall score with bonuses and penalties
                overall_score = (
                    skill_score * 0.4 +
                    proficiency_score * 0.3 +
                    availability_score * 0.2 +
                    capacity_score * 0.1
                ) + domain_bonus - conflict_penalty
                
                # Ensure score is between 0 and 1
                overall_score = max(0, min(1, overall_score))
                
                match_data = {
                    'employee_id': str(emp_id),
                    'employee_name': str(emp_name),
                    'project_id': str(project_id),
                    'project_title': str(project_title),
                    'skill_match': round(skill_score * 100, 2),
                    'proficiency_match': round(proficiency_score * 100, 2),
                    'availability_match': round(availability_score * 100, 2),
                    'capacity_match': round(capacity_score * 100, 2),
                    'overall_score': round(overall_score * 100, 2),
                    'skills': emp_skills,
                    'role': str(employee.get('Role', '')),
                    'proficiency': str(emp_proficiency),
                    'capacity': emp_capacity,
                    'location': str(employee.get('Location', '')),
                    'domain_bonus': round(domain_bonus * 100, 2),
                    'conflict_penalty': round(conflict_penalty * 100, 2)
                }
                
                project_matches.append(match_data)
                
            except Exception as e:
                print(f"Error processing employee {employee.get('Emp ID', 'Unknown')}: {e}")
                continue
        
        # Sort by overall score and get top matches
        project_matches.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Create intelligent team recommendations
        intelligent_recommendations = create_intelligent_team(project_matches, project_domain, used_employees_global)
        
        results.append({
            'project_id': project_id,
            'project_title': project_title,
            'project_domain': project_domain,
            'project_duration': project_duration,
            'project_deadline': str(project_deadline),
            'matches': project_matches[:10],  # Top 10 matches
            'top_3': intelligent_recommendations[:3],  # Intelligent top 3 recommendations
            'intelligent_team': intelligent_recommendations[:5]  # Full intelligent team
        })
    
    matching_results = results
    return results

def calculate_domain_bonus(emp_skills, project_domain):
    """Calculate domain-specific bonus for better matching"""
    if not emp_skills or not project_domain or pd.isna(project_domain):
        return 0
    
    domain_skill_mapping = {
        'ai/ml': ['AI', 'Machine Learning', 'Python Developer', 'Data Science', 'ML'],
        'web development': ['Backend Developer', 'Full Stack Developer', 'FSD', 'Web Development', 'Frontend'],
        'mobile development': ['Mobile Development', 'UI/UX', 'React Native', 'Mobile App', 'iOS', 'Android'],
        'data science': ['Data Science', 'Python Developer', 'Machine Learning', 'Analytics', 'Big Data'],
        'cloud computing': ['DevOps', 'Cloud Computing', 'Infrastructure', 'AWS', 'Azure'],
        'e-commerce': ['Backend Developer', 'Web Development', 'E-commerce', 'Full Stack Developer']
    }
    
    project_domain_str = str(project_domain).lower()
    
    if project_domain_str in domain_skill_mapping:
        domain_skills = set(skill.lower() for skill in domain_skill_mapping[project_domain_str])
        emp_skills_lower = set(str(skill).lower().strip() for skill in emp_skills if skill)
        domain_intersection = len(emp_skills_lower.intersection(domain_skills))
        return min(0.2, domain_intersection * 0.05)  # Max 20% bonus
    
    return 0

def calculate_conflict_penalty(emp_id, project_conflicts):
    """Calculate penalty for conflicts"""
    if project_conflicts == 'None' or not project_conflicts or pd.isna(project_conflicts):
        return 0
    
    # Convert to string to handle any data type
    conflicts_str = str(project_conflicts)
    emp_id_str = str(emp_id)
    
    # Simple conflict detection - in real implementation, this would be more sophisticated
    if emp_id_str in conflicts_str:
        return 0.3  # 30% penalty for conflicts
    
    return 0

def create_intelligent_team(project_matches, project_domain, global_used_employees):
    """Create intelligent team composition with mixed domains and explanations"""
    recommendations = []
    used_employees = set(global_used_employees)  # Start with globally used employees
    
    # Enhanced domain-specific skill mapping with more precise matching
    domain_skill_mapping = {
        'ai': ['AI', 'Machine Learning', 'ML', 'Data Science', 'Python Developer'],
        'ai/ml': ['AI', 'Machine Learning', 'ML', 'Data Science', 'Python Developer'],
        'web development': ['Backend Developer', 'Full Stack Developer', 'FSD', 'Web Development', 'Frontend'],
        'mobile development': ['Mobile Development', 'UI/UX', 'React Native', 'Mobile App', 'iOS', 'Android'],
        'data science': ['Data Science', 'Python Developer', 'Machine Learning', 'Analytics', 'Big Data'],
        'cloud computing': ['DevOps', 'Cloud Computing', 'Infrastructure', 'AWS', 'Azure'],
        'e-commerce': ['Backend Developer', 'Web Development', 'E-commerce', 'Full Stack Developer']
    }
    
    # Get domain-specific skills with better matching
    domain_skills = set()
    project_domain_lower = project_domain.lower().strip()
    
    # Try exact match first, then partial match
    if project_domain_lower in domain_skill_mapping:
        domain_skills.update(domain_skill_mapping[project_domain_lower])
    else:
        # Try partial matching
        for domain, skills in domain_skill_mapping.items():
            if domain in project_domain_lower or project_domain_lower in domain:
                domain_skills.update(skills)
                break
    
    # If still no match, use a default set
    if not domain_skills:
        domain_skills = {'AI', 'Machine Learning', 'Data Science', 'Python Developer'}
    
    # Separate domain-specific and other matches with better logic
    domain_matches = []
    other_matches = []
    
    for match in project_matches:
        # Check if employee has any domain-specific skills
        has_domain_skill = False
        for skill in match['skills']:
            if any(domain_skill.lower() in skill.lower() for domain_skill in domain_skills):
                has_domain_skill = True
                break
        
        if has_domain_skill:
            domain_matches.append(match)
        else:
            other_matches.append(match)
    
    # Sort domain matches by proficiency level and score
    domain_matches.sort(key=lambda x: (x['proficiency'] == 'Senior', x['proficiency'] == 'Intermediate', x['proficiency'] == 'Beginner', x['overall_score']), reverse=True)
    
    # 1. Find 1 Senior employee with domain skills
    senior_domain_match = next((match for match in domain_matches 
                               if match['proficiency'] == 'Senior' and match['employee_id'] not in used_employees), None)
    if senior_domain_match:
        senior_domain_match['selection_reason'] = f"Senior {project_domain} expert with {', '.join(senior_domain_match['skills'][:3])} skills"
        recommendations.append(senior_domain_match)
        used_employees.add(senior_domain_match['employee_id'])
    
    # 2. Find 1 Intermediate employee with domain skills
    intermediate_domain_match = next((match for match in domain_matches 
                                     if match['proficiency'] == 'Intermediate' and match['employee_id'] not in used_employees), None)
    if intermediate_domain_match:
        intermediate_domain_match['selection_reason'] = f"Intermediate {project_domain} specialist with {', '.join(intermediate_domain_match['skills'][:3])} skills"
        recommendations.append(intermediate_domain_match)
        used_employees.add(intermediate_domain_match['employee_id'])
    
    # 3. Find 1 Beginner employee with domain skills
    beginner_domain_match = next((match for match in domain_matches 
                                 if match['proficiency'] == 'Beginner' and match['employee_id'] not in used_employees), None)
    if beginner_domain_match:
        beginner_domain_match['selection_reason'] = f"Beginner {project_domain} developer for learning and growth"
        recommendations.append(beginner_domain_match)
        used_employees.add(beginner_domain_match['employee_id'])
    
    # If we don't have 3 domain experts, fill with best available domain matches
    while len([r for r in recommendations if any(domain_skill.lower() in skill.lower() for skill in r['skills'] for domain_skill in domain_skills)]) < 3 and len(recommendations) < 5:
        remaining_domain = [match for match in domain_matches if match['employee_id'] not in used_employees]
        if remaining_domain:
            best_domain = remaining_domain[0]
            best_domain['selection_reason'] = f"Additional {project_domain} specialist with {', '.join(best_domain['skills'][:3])} skills"
            recommendations.append(best_domain)
            used_employees.add(best_domain['employee_id'])
        else:
            break
    
    # 4. Add 2 employees from other domains for complementary skills
    complementary_roles = {
        'ai': ['Backend Developer', 'UI/UX', 'Project Manager', 'DevOps'],
        'ai/ml': ['Backend Developer', 'UI/UX', 'Project Manager', 'DevOps'],
        'web development': ['UI/UX', 'DevOps', 'Project Manager', 'Backend Developer'],
        'mobile development': ['Backend Developer', 'UI/UX', 'DevOps', 'Project Manager'],
        'data science': ['Backend Developer', 'UI/UX', 'DevOps', 'Project Manager'],
        'cloud computing': ['Backend Developer', 'Project Manager', 'UI/UX', 'DevOps'],
        'e-commerce': ['UI/UX', 'DevOps', 'Project Manager', 'Backend Developer']
    }
    
    complementary_skills = complementary_roles.get(project_domain_lower, ['Backend Developer', 'UI/UX', 'Project Manager', 'DevOps'])
    
    # Sort other matches by score
    other_matches.sort(key=lambda x: x['overall_score'], reverse=True)
    
    # Find exactly 2 complementary employees
    complementary_count = 0
    for skill in complementary_skills:
        if complementary_count >= 2 or len(recommendations) >= 5:
            break
            
        complementary_match = next((match for match in other_matches 
                                   if any(s.lower() in skill.lower() or skill.lower() in s.lower() for s in match['skills']) and 
                                   match['employee_id'] not in used_employees and
                                   match['overall_score'] >= 40), None)
        
        if complementary_match:
            if skill == 'UI/UX':
                complementary_match['selection_reason'] = f"UI/UX designer for user interface and experience design"
            elif skill == 'Backend Developer':
                complementary_match['selection_reason'] = f"Backend developer for API development and database management"
            elif skill == 'DevOps':
                complementary_match['selection_reason'] = f"DevOps engineer for deployment and infrastructure management"
            elif skill == 'Project Manager':
                complementary_match['selection_reason'] = f"Project manager for coordination and project oversight"
            else:
                complementary_match['selection_reason'] = f"Complementary skill specialist for {skill}"
            
            recommendations.append(complementary_match)
            used_employees.add(complementary_match['employee_id'])
            complementary_count += 1
    
    # 5. Fill remaining slots with best available matches if we don't have 5 yet
    if len(recommendations) < 5:
        remaining_matches = [match for match in project_matches if match['employee_id'] not in used_employees]
        remaining_matches.sort(key=lambda x: x['overall_score'], reverse=True)
        
        for match in remaining_matches[:5-len(recommendations)]:
            if match['overall_score'] >= 50:
                match['selection_reason'] = f"High-performing team member with {', '.join(match['skills'][:2])} skills"
                recommendations.append(match)
                used_employees.add(match['employee_id'])
    
    # Update global used employees with newly selected employees
    for rec in recommendations:
        global_used_employees.add(rec['employee_id'])
    
    return recommendations

@app.route('/')
def index():
    """Main page with title and get started button"""
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/login')
def login_page():
    """Login page"""
    if is_logged_in():
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    """Signup page"""
    if is_logged_in():
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()  # Clear all session data
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/clear-session')
def clear_session():
    """Clear session for debugging"""
    session.clear()
    flash('Session cleared!', 'info')
    return redirect(url_for('index'))

@app.route('/test-login')
def test_login():
    """Test login page"""
    return f"<h1>Test Login Page</h1><p>User logged in: {is_logged_in()}</p><p>Current user: {get_current_user()}</p><a href='/'>Back to Home</a>"

@app.route('/test-signup')
def test_signup():
    """Test signup page"""
    return f"<h1>Test Signup Page</h1><p>User logged in: {is_logged_in()}</p><p>Current user: {get_current_user()}</p><a href='/'>Back to Home</a>"


@app.route('/dashboard')
def dashboard():
    """Dashboard page with key features and how it works"""
    user = get_current_user()
    return render_template('dashboard.html', user=user)

@app.route('/prototype')
def prototype():
    """Prototype page with upload interface"""
    if not is_logged_in():
        flash('Please log in to access the prototype', 'info')
        return redirect(url_for('login_page'))
    
    user = get_current_user()
    return render_template('prototype.html', user=user)

@app.route('/results')
def results():
    """Results page showing matching results"""
    if not is_logged_in():
        flash('Please log in to view results', 'info')
        return redirect(url_for('login_page'))
    
    user = get_current_user()
    return render_template('results.html', user=user)

@app.route('/api/login', methods=['POST'])
def login():
    """Handle login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password are required"})
        
        # Find user by email
        user = None
        for user_id, user_data in users_db.items():
            if user_data['email'] == email:
                user = user_data
                break
        
        if not user or not verify_password(password, user['password']):
            return jsonify({"status": "error", "message": "Invalid email or password"})
        
        # Set session
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        
        return jsonify({"status": "success", "message": "Login successful", "redirect": url_for('index')})
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Login failed: {str(e)}"})

@app.route('/api/signup', methods=['POST'])
def signup():
    """Handle signup"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not name or not email or not password:
            return jsonify({"status": "error", "message": "All fields are required"})
        
        if password != confirm_password:
            return jsonify({"status": "error", "message": "Passwords do not match"})
        
        if len(password) < 6:
            return jsonify({"status": "error", "message": "Password must be at least 6 characters long"})
        
        # Check if user already exists
        for user_data in users_db.values():
            if user_data['email'] == email:
                return jsonify({"status": "error", "message": "Email already registered"})
        
        # Create new user
        user_id = secrets.token_hex(16)
        user = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().isoformat()
        }
        users_db[user_id] = user
        
        # Set session
        session['user_id'] = user_id
        session['user_name'] = name
        
        return jsonify({"status": "success", "message": "Account created successfully", "redirect": url_for('index')})
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Signup failed: {str(e)}"})

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        if not is_logged_in():
            return jsonify({"status": "error", "message": "Please log in to upload files"})
        
        if 'employees' in request.files:
            employees_file = request.files['employees']
            if employees_file.filename != '':
                employees_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'Employees.csv'))
        
        if 'projects' in request.files:
            projects_file = request.files['projects']
            if projects_file.filename != '':
                projects_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'Projects.csv'))
        
        # Reload data after upload
        load_data()
        
        return jsonify({"status": "success", "message": "Files uploaded successfully"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/match', methods=['POST'])
def match_resources():
    """Perform resource matching"""
    try:
        if employees_df is None or employees_df.empty:
            return jsonify({"status": "error", "message": "No employee data available. Please upload employee data first."})
        
        if projects_df is None or projects_df.empty:
            return jsonify({"status": "error", "message": "No project data available. Please upload project data first."})
        
        results = perform_matching()
        
        if "error" in results:
            return jsonify({"status": "error", "message": results["error"]})
        
        return jsonify({"status": "success", "data": results})
    
    except Exception as e:
        print(f"Error in match_resources: {e}")
        return jsonify({"status": "error", "message": f"Error performing matching: {str(e)}"})

@app.route('/api/data')
def get_data():
    """Get current data status"""
    return jsonify({
        "employees_loaded": employees_df is not None and not employees_df.empty,
        "projects_loaded": projects_df is not None and not projects_df.empty,
        "employees_count": len(employees_df) if employees_df is not None else 0,
        "projects_count": len(projects_df) if projects_df is not None else 0
    })

@app.route('/api/results')
def get_results():
    """Get matching results"""
    if matching_results is None:
        return jsonify({"status": "error", "message": "No matching results available"})
    
    return jsonify({"status": "success", "data": matching_results})

@app.route('/api/download-pdf')
def download_pdf():
    """Generate and download detailed PDF report"""
    if matching_results is None:
        return jsonify({"status": "error", "message": "No matching results available"})
    
    try:
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,
            textColor=colors.HexColor('#667eea')
        )
        story.append(Paragraph("AI Talent Management System - Detailed Report", title_style))
        story.append(Spacer(1, 20))
        
        # Summary section
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        total_projects = len(matching_results)
        
        # Calculate unique employees assigned to intelligent teams
        assigned_employees = set()
        for project in matching_results:
            intelligent_team = project.get('intelligent_team', project.get('top_3', []))
            for match in intelligent_team:
                assigned_employees.add(match['employee_id'])
        
        total_employees = len(assigned_employees)
        avg_score = sum(match['overall_score'] for project in matching_results for match in project['matches']) / sum(len(project['matches']) for project in matching_results) if matching_results else 0
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Projects Analyzed', str(total_projects)],
            ['Unique Employees Assigned', str(total_employees)],
            ['Average Match Score', f"{avg_score:.1f}%"],
            ['No Duplicates', '✓ Each employee assigned to only one project'],
            ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Project-wise recommendations
        story.append(Paragraph("Project-wise Recommendations", styles['Heading2']))
        
        for i, project in enumerate(matching_results, 1):
            story.append(Paragraph(f"{i}. {project['project_title']}", styles['Heading3']))
            story.append(Paragraph(f"Domain: {project['project_domain']} | Duration: {project['project_duration']} weeks", styles['Normal']))
            story.append(Paragraph(f"Deadline: {project['project_deadline']}", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Top recommendations table
            recommendations = project.get('intelligent_team', project.get('top_3', []))[:5]
            if recommendations:
                rec_data = [['Rank', 'Employee', 'Role', 'Proficiency', 'Score', 'Selection Reason']]
                for j, match in enumerate(recommendations, 1):
                    reason = match.get('selection_reason', 'High-performing team member')
                    rec_data.append([
                        str(j),
                        match['employee_name'],
                        match['role'],
                        match['proficiency'],
                        f"{match['overall_score']}%",
                        reason[:50] + "..." if len(reason) > 50 else reason
                    ])
                
                rec_table = Table(rec_data, colWidths=[0.5*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.5*inch, 2*inch])
                rec_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                story.append(rec_table)
            else:
                story.append(Paragraph("No recommendations available for this project.", styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # Analytics section
        story.append(Paragraph("Analytics Summary", styles['Heading2']))
        
        # Role distribution
        role_counts = {}
        for project in matching_results:
            for match in project['matches']:
                role_counts[match['role']] = role_counts.get(match['role'], 0) + 1
        
        if role_counts:
            story.append(Paragraph("Employee Distribution by Role", styles['Heading3']))
            role_data = [['Role', 'Count', 'Percentage']]
            total_matches = sum(role_counts.values())
            for role, count in role_counts.items():
                percentage = (count / total_matches) * 100
                role_data.append([role, str(count), f"{percentage:.1f}%"])
            
            role_table = Table(role_data)
            role_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(role_table)
            story.append(Spacer(1, 15))
        
        # Domain distribution
        domain_counts = {}
        for project in matching_results:
            domain_counts[project['project_domain']] = domain_counts.get(project['project_domain'], 0) + 1
        
        if domain_counts:
            story.append(Paragraph("Project Distribution by Domain", styles['Heading3']))
            domain_data = [['Domain', 'Project Count']]
            for domain, count in domain_counts.items():
                domain_data.append([domain, str(count)])
            
            domain_table = Table(domain_data)
            domain_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f093fb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(domain_table)
            story.append(Spacer(1, 15))
        
        # Score distribution
        score_ranges = {'90-100%': 0, '80-89%': 0, '70-79%': 0, '60-69%': 0, 'Below 60%': 0}
        for project in matching_results:
            for match in project['matches']:
                score = match['overall_score']
                if score >= 90: score_ranges['90-100%'] += 1
                elif score >= 80: score_ranges['80-89%'] += 1
                elif score >= 70: score_ranges['70-79%'] += 1
                elif score >= 60: score_ranges['60-69%'] += 1
                else: score_ranges['Below 60%'] += 1
        
        story.append(Paragraph("Match Score Distribution", styles['Heading3']))
        score_data = [['Score Range', 'Count', 'Percentage']]
        total_scores = sum(score_ranges.values())
        for range_name, count in score_ranges.items():
            percentage = (count / total_scores) * 100 if total_scores > 0 else 0
            score_data.append([range_name, str(count), f"{percentage:.1f}%"])
        
        score_table = Table(score_data)
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4facfe')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("Generated by AI Talent Management System", styles['Normal']))
        story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Return PDF as response
        from flask import Response
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=talent_management_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            }
        )
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error generating PDF: {str(e)}"})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI-Driven Talent Management System")
    print("=" * 60)
    print("Starting application...")
    
    # Create datasets directory if it doesn't exist
    os.makedirs('datasets', exist_ok=True)
    print("📁 Created datasets directory")
    
    # Load initial data
    print("📊 Loading data...")
    load_data()
    
    print("✅ Application ready!")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("=" * 60)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
