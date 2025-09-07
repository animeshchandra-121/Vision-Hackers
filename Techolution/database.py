"""
Database module for AI-Driven Talent Management System
Handles database operations for employees and projects data
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict, Optional, Tuple
import logging

def convert_to_date_string(date_value):
    """Convert various date formats to string"""
    if pd.isna(date_value) or date_value == '' or date_value is None:
        return None
    
    try:
        # If it's already a string, return as is
        if isinstance(date_value, str):
            return date_value
        
        # If it's a pandas Timestamp or datetime, convert to string
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%Y-%m-%d')
        
        # Try to convert to string
        return str(date_value)
    except Exception:
        return None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for handling all database operations"""
    
    def __init__(self, db_path: str = "talent_management.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create employees table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS employees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        emp_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        skills TEXT NOT NULL,
                        role TEXT NOT NULL,
                        capacity_per_week REAL NOT NULL,
                        previous_project_description TEXT,
                        proficiency TEXT NOT NULL,
                        available_date DATE,
                        location TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create projects table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id TEXT UNIQUE NOT NULL,
                        project_title TEXT NOT NULL,
                        domain TEXT NOT NULL,
                        eligibility TEXT NOT NULL,
                        duration TEXT NOT NULL,
                        proficiency TEXT NOT NULL,
                        conflicts TEXT,
                        hard_deadline DATE NOT NULL,
                        experience_years INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create employee_skills table for normalized skill storage
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS employee_skills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER NOT NULL,
                        skill TEXT NOT NULL,
                        FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE,
                        UNIQUE(employee_id, skill)
                    )
                ''')
                
                # Create project_requirements table for normalized requirements storage
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS project_requirements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        requirement TEXT NOT NULL,
                        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                        UNIQUE(project_id, requirement)
                    )
                ''')
                
                # Create matching_results table to store matching history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS matching_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER NOT NULL,
                        project_id INTEGER NOT NULL,
                        skill_match REAL NOT NULL,
                        proficiency_match REAL NOT NULL,
                        availability_match REAL NOT NULL,
                        capacity_match REAL NOT NULL,
                        overall_score REAL NOT NULL,
                        domain_bonus REAL DEFAULT 0,
                        conflict_penalty REAL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE,
                        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_emp_id ON employees(emp_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_skills ON employees(skills)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_proficiency ON employees(proficiency)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_available_date ON employees(available_date)')
                
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_project_id ON projects(project_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_domain ON projects(domain)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_proficiency ON projects(proficiency)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_deadline ON projects(hard_deadline)')
                
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_skills_employee_id ON employee_skills(employee_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_skills_skill ON employee_skills(skill)')
                
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_requirements_project_id ON project_requirements(project_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_requirements_requirement ON project_requirements(requirement)')
                
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_matching_results_employee_id ON matching_results(employee_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_matching_results_project_id ON matching_results(project_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_matching_results_overall_score ON matching_results(overall_score)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def insert_employee(self, emp_data: Dict) -> int:
        """Insert a single employee record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert employee
                cursor.execute('''
                    INSERT OR REPLACE INTO employees 
                    (emp_id, name, skills, role, capacity_per_week, previous_project_description, 
                     proficiency, available_date, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    emp_data['emp_id'],
                    emp_data['name'],
                    emp_data['skills'],
                    emp_data['role'],
                    emp_data['capacity_per_week'],
                    emp_data.get('previous_project_description', ''),
                    emp_data['proficiency'],
                    emp_data.get('available_date'),
                    emp_data['location']
                ))
                
                employee_id = cursor.lastrowid
                
                # Insert normalized skills
                if 'skills' in emp_data and emp_data['skills']:
                    skills = [skill.strip() for skill in str(emp_data['skills']).split(',') if skill.strip()]
                    for skill in skills:
                        cursor.execute('''
                            INSERT OR IGNORE INTO employee_skills (employee_id, skill)
                            VALUES (?, ?)
                        ''', (employee_id, skill))
                
                conn.commit()
                return employee_id
                
        except Exception as e:
            logger.error(f"Error inserting employee: {e}")
            raise
    
    def insert_project(self, project_data: Dict) -> int:
        """Insert a single project record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert project
                cursor.execute('''
                    INSERT OR REPLACE INTO projects 
                    (project_id, project_title, domain, eligibility, duration, proficiency, 
                     conflicts, hard_deadline, experience_years)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    project_data['project_id'],
                    project_data['project_title'],
                    project_data['domain'],
                    project_data['eligibility'],
                    project_data['duration'],
                    project_data['proficiency'],
                    project_data.get('conflicts', ''),
                    project_data['hard_deadline'],
                    project_data['experience_years']
                ))
                
                project_id = cursor.lastrowid
                
                # Insert normalized requirements
                if 'eligibility' in project_data and project_data['eligibility']:
                    requirements = [req.strip() for req in str(project_data['eligibility']).split(',') if req.strip()]
                    for requirement in requirements:
                        cursor.execute('''
                            INSERT OR IGNORE INTO project_requirements (project_id, requirement)
                            VALUES (?, ?)
                        ''', (project_id, requirement))
                
                conn.commit()
                return project_id
                
        except Exception as e:
            logger.error(f"Error inserting project: {e}")
            raise
    
    def bulk_insert_employees(self, employees_df: pd.DataFrame) -> int:
        """Bulk insert employees from DataFrame"""
        try:
            count = 0
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for _, row in employees_df.iterrows():
                    emp_data = {
                        'emp_id': str(row.get('Emp ID', '')),
                        'name': str(row.get('Name', '')),
                        'skills': str(row.get('Skills', '')),
                        'role': str(row.get('Role', '')),
                        'capacity_per_week': float(row.get('Capacity per week (hrs)', 0)),
                        'previous_project_description': str(row.get('Previous Project Description', '')),
                        'proficiency': str(row.get('Proficiency', '')),
                        'available_date': convert_to_date_string(row.get('Available Date', '')),
                        'location': str(row.get('Location', ''))
                    }
                    
                    # Insert employee
                    cursor.execute('''
                        INSERT OR REPLACE INTO employees 
                        (emp_id, name, skills, role, capacity_per_week, previous_project_description, 
                         proficiency, available_date, location)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        emp_data['emp_id'],
                        emp_data['name'],
                        emp_data['skills'],
                        emp_data['role'],
                        emp_data['capacity_per_week'],
                        emp_data['previous_project_description'],
                        emp_data['proficiency'],
                        emp_data['available_date'],
                        emp_data['location']
                    ))
                    
                    employee_id = cursor.lastrowid
                    
                    # Insert normalized skills
                    if emp_data['skills']:
                        skills = [skill.strip() for skill in str(emp_data['skills']).split(',') if skill.strip()]
                        for skill in skills:
                            cursor.execute('''
                                INSERT OR IGNORE INTO employee_skills (employee_id, skill)
                                VALUES (?, ?)
                            ''', (employee_id, skill))
                    
                    count += 1
                
                conn.commit()
                logger.info(f"Bulk inserted {count} employees")
                return count
                
        except Exception as e:
            logger.error(f"Error bulk inserting employees: {e}")
            raise
    
    def bulk_insert_projects(self, projects_df: pd.DataFrame) -> int:
        """Bulk insert projects from DataFrame"""
        try:
            count = 0
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for _, row in projects_df.iterrows():
                    project_data = {
                        'project_id': str(row.get('ID', '')),
                        'project_title': str(row.get('Project_Title', '')),
                        'domain': str(row.get('Domain', '')),
                        'eligibility': str(row.get('Eligibility', '')),
                        'duration': str(row.get('Duration', '')),
                        'proficiency': str(row.get('Proficiency', '')),
                        'conflicts': str(row.get('Conflicts', '')),
                        'hard_deadline': convert_to_date_string(row.get('Hard_Deadline', '')),
                        'experience_years': int(row.get('Experience_years', 0))
                    }
                    
                    # Insert project
                    cursor.execute('''
                        INSERT OR REPLACE INTO projects 
                        (project_id, project_title, domain, eligibility, duration, proficiency, 
                         conflicts, hard_deadline, experience_years)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        project_data['project_id'],
                        project_data['project_title'],
                        project_data['domain'],
                        project_data['eligibility'],
                        project_data['duration'],
                        project_data['proficiency'],
                        project_data['conflicts'],
                        project_data['hard_deadline'],
                        project_data['experience_years']
                    ))
                    
                    project_id = cursor.lastrowid
                    
                    # Insert normalized requirements
                    if project_data['eligibility']:
                        requirements = [req.strip() for req in str(project_data['eligibility']).split(',') if req.strip()]
                        for requirement in requirements:
                            cursor.execute('''
                                INSERT OR IGNORE INTO project_requirements (project_id, requirement)
                                VALUES (?, ?)
                            ''', (project_id, requirement))
                    
                    count += 1
                
                conn.commit()
                logger.info(f"Bulk inserted {count} projects")
                return count
                
        except Exception as e:
            logger.error(f"Error bulk inserting projects: {e}")
            raise
    
    def get_all_employees(self) -> pd.DataFrame:
        """Get all employees as DataFrame"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT emp_id, name, skills, role, capacity_per_week, 
                           previous_project_description, proficiency, available_date, location
                    FROM employees
                    ORDER BY emp_id
                '''
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error getting employees: {e}")
            return pd.DataFrame()
    
    def get_all_projects(self) -> pd.DataFrame:
        """Get all projects as DataFrame"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT project_id, project_title, domain, eligibility, duration, 
                           proficiency, conflicts, hard_deadline, experience_years
                    FROM projects
                    ORDER BY project_id
                '''
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return pd.DataFrame()
    
    def get_employee_by_id(self, emp_id: str) -> Optional[Dict]:
        """Get employee by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM employees WHERE emp_id = ?
                ''', (emp_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"Error getting employee by ID: {e}")
            return None
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM projects WHERE project_id = ?
                ''', (project_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"Error getting project by ID: {e}")
            return None
    
    def get_employee_skills(self, emp_id: str) -> List[str]:
        """Get employee skills"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT es.skill FROM employee_skills es
                    JOIN employees e ON es.employee_id = e.id
                    WHERE e.emp_id = ?
                ''', (emp_id,))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting employee skills: {e}")
            return []
    
    def get_project_requirements(self, project_id: str) -> List[str]:
        """Get project requirements"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT pr.requirement FROM project_requirements pr
                    JOIN projects p ON pr.project_id = p.id
                    WHERE p.project_id = ?
                ''', (project_id,))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting project requirements: {e}")
            return []
    
    def save_matching_result(self, employee_id: int, project_id: int, scores: Dict) -> int:
        """Save matching result"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO matching_results 
                    (employee_id, project_id, skill_match, proficiency_match, 
                     availability_match, capacity_match, overall_score, domain_bonus, conflict_penalty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    employee_id, project_id,
                    scores.get('skill_match', 0),
                    scores.get('proficiency_match', 0),
                    scores.get('availability_match', 0),
                    scores.get('capacity_match', 0),
                    scores.get('overall_score', 0),
                    scores.get('domain_bonus', 0),
                    scores.get('conflict_penalty', 0)
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving matching result: {e}")
            raise
    
    def get_matching_history(self, limit: int = 100) -> pd.DataFrame:
        """Get matching history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT mr.*, e.emp_id, e.name as employee_name, 
                           p.project_id, p.project_title
                    FROM matching_results mr
                    JOIN employees e ON mr.employee_id = e.id
                    JOIN projects p ON mr.project_id = p.id
                    ORDER BY mr.created_at DESC
                    LIMIT ?
                '''
                return pd.read_sql_query(query, conn, params=(limit,))
        except Exception as e:
            logger.error(f"Error getting matching history: {e}")
            return pd.DataFrame()
    
    def clear_all_data(self):
        """Clear all data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM matching_results')
                cursor.execute('DELETE FROM project_requirements')
                cursor.execute('DELETE FROM employee_skills')
                cursor.execute('DELETE FROM projects')
                cursor.execute('DELETE FROM employees')
                conn.commit()
                logger.info("All data cleared from database")
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            raise
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count employees
                cursor.execute('SELECT COUNT(*) FROM employees')
                stats['employees_count'] = cursor.fetchone()[0]
                
                # Count projects
                cursor.execute('SELECT COUNT(*) FROM projects')
                stats['projects_count'] = cursor.fetchone()[0]
                
                # Count skills
                cursor.execute('SELECT COUNT(*) FROM employee_skills')
                stats['skills_count'] = cursor.fetchone()[0]
                
                # Count requirements
                cursor.execute('SELECT COUNT(*) FROM project_requirements')
                stats['requirements_count'] = cursor.fetchone()[0]
                
                # Count matching results
                cursor.execute('SELECT COUNT(*) FROM matching_results')
                stats['matching_results_count'] = cursor.fetchone()[0]
                
                return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

# Global database instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    return db_manager
