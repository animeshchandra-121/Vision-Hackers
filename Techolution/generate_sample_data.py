#!/usr/bin/env python3
"""
Generate sample data for testing the AI Talent Management System
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import os

def generate_employees_data():
    """Generate sample employees data"""
    skills_options = [
        'Backend Developer', 'Python Developer', 'Project Manager', 
        'AI', 'UI/UX', 'FSD', 'Data Science', 'Machine Learning',
        'DevOps', 'Cloud Computing', 'Mobile Development', 'Web Development'
    ]
    
    roles = ['Intern', 'Full Time', 'Senior']
    proficiencies = ['Beginner', 'Intermediate', 'Senior']
    locations = ['India', 'USA', 'UK', 'Canada', 'Australia']
    
    employees = []
    
    for i in range(50):  # Generate 50 employees
        emp_id = f"E{i+1:03d}"
        name = f"Employee {i+1}"
        
        # Randomly select 2-4 skills
        num_skills = random.randint(2, 4)
        skills = random.sample(skills_options, num_skills)
        skills_str = ', '.join(skills)
        
        role = random.choice(roles)
        proficiency = random.choice(proficiencies)
        capacity = random.randint(20, 50)  # 20-50 hours per week
        
        # Generate previous project description
        project_types = ['E-commerce', 'Mobile App', 'Web Platform', 'Data Analysis', 'AI Model', 'Cloud Migration']
        project_desc = f"Worked on {random.choice(project_types)} project"
        
        # Generate available date (some in past, some in future)
        if random.random() < 0.7:  # 70% available now
            available_date = datetime.now() - timedelta(days=random.randint(1, 30))
        else:  # 30% available in future
            available_date = datetime.now() + timedelta(days=random.randint(1, 60))
        
        location = random.choice(locations)
        
        employees.append({
            'Emp ID': emp_id,
            'Name': name,
            'Skills': skills_str,
            'Role': role,
            'Capacity per week (hrs)': capacity,
            'Previous Project Description': project_desc,
            'Proficiency': proficiency,
            'Available Date': available_date.strftime('%Y-%m-%d'),
            'Location': location
        })
    
    return pd.DataFrame(employees)

def generate_projects_data():
    """Generate sample projects data"""
    domains = [
        'AI/ML', 'Web Development', 'Mobile Development', 'Data Science',
        'Cloud Computing', 'DevOps', 'E-commerce', 'FinTech', 'HealthTech'
    ]
    
    project_titles = [
        'AI Chatbot Development', 'E-commerce Platform', 'Mobile Banking App',
        'Data Analytics Dashboard', 'Cloud Migration Project', 'ML Model Training',
        'Web Application Redesign', 'IoT Integration', 'Blockchain Implementation',
        'API Development', 'Database Optimization', 'Security Enhancement'
    ]
    
    eligibilities = ['All', 'Senior,Intermediate', 'Intern,Full Time', 'Senior', 'Full Time,Intern']
    proficiencies = ['Beginner', 'Intermediate', 'Senior']
    conflicts = ['None', 'P001', 'P002', 'P003', 'P004']
    
    projects = []
    
    for i in range(15):  # Generate 15 projects
        project_id = f"P{i+1:03d}"
        title = random.choice(project_titles)
        domain = random.choice(domains)
        eligibility = random.choice(eligibilities)
        duration = random.randint(4, 24)  # 4-24 weeks
        proficiency = random.choice(proficiencies)
        conflict = random.choice(conflicts)
        
        # Generate deadline (1-6 months from now)
        deadline = datetime.now() + timedelta(days=random.randint(30, 180))
        
        experience_years = random.randint(1, 5)
        
        projects.append({
            'ID': project_id,
            'Project_Title': title,
            'Domain': domain,
            'Eligibility': eligibility,
            'Duration': duration,
            'Proficiency': proficiency,
            'Conflicts': conflict,
            'Hard_Deadline': deadline.strftime('%Y-%m-%d'),
            'Experience_years': experience_years
        })
    
    return pd.DataFrame(projects)

def main():
    """Generate sample data files"""
    print("Generating sample data for AI Talent Management System...")
    
    # Create datasets directory if it doesn't exist
    os.makedirs('datasets', exist_ok=True)
    
    # Generate employees data
    print("Generating employees data...")
    employees_df = generate_employees_data()
    employees_df.to_csv('datasets/Employees.csv', index=False)
    print(f"✓ Generated {len(employees_df)} employees")
    
    # Generate projects data
    print("Generating projects data...")
    projects_df = generate_projects_data()
    projects_df.to_csv('datasets/Projects.csv', index=False)
    print(f"✓ Generated {len(projects_df)} projects")
    
    print("\nSample data generated successfully!")
    print("Files created:")
    print("- datasets/Employees.csv")
    print("- datasets/Projects.csv")
    print("\nYou can now run the application with: python app.py")

if __name__ == "__main__":
    main()
