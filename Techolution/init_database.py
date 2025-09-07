"""
Database initialization script for AI-Driven Talent Management System
This script initializes the database and migrates existing CSV data
"""

import os
import sys
import pandas as pd
from datetime import datetime
import logging
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database and migrate existing data"""
    try:
        logger.info("🚀 Starting database initialization...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        logger.info("✅ Database manager initialized")
        
        # Check if CSV files exist
        employees_csv_path = 'datasets/Employees.csv'
        projects_csv_path = 'datasets/Projects.csv'
        
        employees_exists = os.path.exists(employees_csv_path)
        projects_exists = os.path.exists(projects_csv_path)
        
        logger.info(f"📁 Employees CSV exists: {employees_exists}")
        logger.info(f"📁 Projects CSV exists: {projects_exists}")
        
        # Migrate employees data
        if employees_exists:
            logger.info("📊 Migrating employees data...")
            try:
                employees_df = pd.read_csv(employees_csv_path)
                logger.info(f"📋 Loaded {len(employees_df)} employee records")
                
                # Clean and validate data
                employees_df = clean_employees_data(employees_df)
                
                # Insert into database
                count = db_manager.bulk_insert_employees(employees_df)
                logger.info(f"✅ Successfully migrated {count} employees to database")
                
            except Exception as e:
                logger.error(f"❌ Error migrating employees: {e}")
                return False
        else:
            logger.warning("⚠️ No employees CSV found, skipping employees migration")
        
        # Migrate projects data
        if projects_exists:
            logger.info("📊 Migrating projects data...")
            try:
                projects_df = pd.read_csv(projects_csv_path)
                logger.info(f"📋 Loaded {len(projects_df)} project records")
                
                # Clean and validate data
                projects_df = clean_projects_data(projects_df)
                
                # Insert into database
                count = db_manager.bulk_insert_projects(projects_df)
                logger.info(f"✅ Successfully migrated {count} projects to database")
                
            except Exception as e:
                logger.error(f"❌ Error migrating projects: {e}")
                return False
        else:
            logger.warning("⚠️ No projects CSV found, skipping projects migration")
        
        # Get database statistics
        stats = db_manager.get_database_stats()
        logger.info("📈 Database Statistics:")
        logger.info(f"   👥 Employees: {stats.get('employees_count', 0)}")
        logger.info(f"   📋 Projects: {stats.get('projects_count', 0)}")
        logger.info(f"   🎯 Skills: {stats.get('skills_count', 0)}")
        logger.info(f"   📝 Requirements: {stats.get('requirements_count', 0)}")
        logger.info(f"   🔗 Matching Results: {stats.get('matching_results_count', 0)}")
        
        logger.info("🎉 Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def clean_employees_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate employees data"""
    logger.info("🧹 Cleaning employees data...")
    
    # Handle missing values
    df = df.fillna('')
    
    # Convert data types
    if 'Capacity per week (hrs)' in df.columns:
        df['Capacity per week (hrs)'] = pd.to_numeric(df['Capacity per week (hrs)'], errors='coerce').fillna(0)
    
    # Clean date column
    if 'Available Date' in df.columns:
        df['Available Date'] = pd.to_datetime(df['Available Date'], errors='coerce')
    
    # Clean text columns
    text_columns = ['Name', 'Skills', 'Role', 'Previous Project Description', 'Proficiency', 'Location']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Remove duplicates based on Emp ID
    if 'Emp ID' in df.columns:
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Emp ID'], keep='first')
        final_count = len(df)
        if initial_count != final_count:
            logger.info(f"🔄 Removed {initial_count - final_count} duplicate employee records")
    
    logger.info(f"✅ Cleaned {len(df)} employee records")
    return df

def clean_projects_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate projects data"""
    logger.info("🧹 Cleaning projects data...")
    
    # Handle missing values
    df = df.fillna('')
    
    # Convert data types
    if 'Experience_years' in df.columns:
        df['Experience_years'] = pd.to_numeric(df['Experience_years'], errors='coerce').fillna(0).astype(int)
    
    # Clean date column
    if 'Hard_Deadline' in df.columns:
        df['Hard_Deadline'] = pd.to_datetime(df['Hard_Deadline'], errors='coerce')
    
    # Clean text columns
    text_columns = ['ID', 'Project_Title', 'Domain', 'Eligibility', 'Duration', 'Proficiency', 'Conflicts']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Remove duplicates based on ID
    if 'ID' in df.columns:
        initial_count = len(df)
        df = df.drop_duplicates(subset=['ID'], keep='first')
        final_count = len(df)
        if initial_count != final_count:
            logger.info(f"🔄 Removed {initial_count - final_count} duplicate project records")
    
    logger.info(f"✅ Cleaned {len(df)} project records")
    return df

def create_sample_data():
    """Create sample data if no CSV files exist"""
    logger.info("🎭 Creating sample data...")
    
    db_manager = DatabaseManager()
    
    # Create sample employees
    sample_employees = pd.DataFrame({
        'Emp ID': ['E001', 'E002', 'E003', 'E004', 'E005'],
        'Name': ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'David Brown'],
        'Skills': ['Backend Developer,Python Developer', 'AI,Python Developer', 'UI/UX,FSD', 
                  'Project Manager', 'Backend Developer,AI'],
        'Role': ['Senior', 'Full Time', 'Intern', 'Senior', 'Full Time'],
        'Capacity per week (hrs)': [40, 35, 20, 40, 35],
        'Previous Project Description': ['E-commerce platform', 'ML model development', 'Mobile app design', 
                                       'Team management', 'Data analysis'],
        'Proficiency': ['Senior', 'Intermediate', 'Beginner', 'Senior', 'Intermediate'],
        'Available Date': ['2024-01-01', '2024-01-15', '2024-02-01', '2024-01-01', '2024-01-10'],
        'Location': ['India', 'India', 'India', 'India', 'India']
    })
    
    # Create sample projects
    sample_projects = pd.DataFrame({
        'ID': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'Project_Title': ['AI Chatbot Development', 'E-commerce Platform', 'Mobile App Design', 
                         'Data Analytics Dashboard', 'Cloud Migration Project'],
        'Domain': ['AI/ML', 'Web Development', 'Mobile Development', 'Data Science', 'Cloud Computing'],
        'Eligibility': ['Senior,Intermediate', 'All', 'Intern,Full Time', 'Senior,Intermediate', 'Senior,Full Time'],
        'Duration': ['12 weeks', '8 weeks', '6 weeks', '10 weeks', '16 weeks'],
        'Proficiency': ['Senior', 'Intermediate', 'Beginner', 'Senior', 'Senior'],
        'Conflicts': ['None', 'P001', 'None', 'P002', 'None'],
        'Hard_Deadline': ['2024-06-01', '2024-04-15', '2024-03-30', '2024-05-20', '2024-07-10'],
        'Experience_years': [3, 2, 1, 4, 5]
    })
    
    # Insert sample data
    try:
        count_emp = db_manager.bulk_insert_employees(sample_employees)
        count_proj = db_manager.bulk_insert_projects(sample_projects)
        logger.info(f"✅ Created {count_emp} sample employees and {count_proj} sample projects")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}")
        return False

def reset_database():
    """Reset database (clear all data)"""
    try:
        logger.info("🔄 Resetting database...")
        db_manager = DatabaseManager()
        db_manager.clear_all_data()
        logger.info("✅ Database reset completed")
        return True
    except Exception as e:
        logger.error(f"❌ Error resetting database: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🗄️ AI-Driven Talent Management System - Database Initialization")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'reset':
            success = reset_database()
        elif command == 'sample':
            success = create_sample_data()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: reset, sample")
            success = False
    else:
        # Default: initialize database
        success = initialize_database()
    
    if success:
        print("🎉 Operation completed successfully!")
    else:
        print("❌ Operation failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
