"""
Data Migration Script for AI-Driven Talent Management System
This script helps migrate existing CSV data to the database
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

def migrate_csv_to_database():
    """Migrate existing CSV files to database"""
    try:
        logger.info("🔄 Starting CSV to Database migration...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Check for existing CSV files
        employees_csv_path = 'datasets/Employees.csv'
        projects_csv_path = 'datasets/Projects.csv'
        
        employees_exists = os.path.exists(employees_csv_path)
        projects_exists = os.path.exists(projects_csv_path)
        
        logger.info(f"📁 Employees CSV exists: {employees_exists}")
        logger.info(f"📁 Projects CSV exists: {projects_exists}")
        
        if not employees_exists and not projects_exists:
            logger.warning("⚠️ No CSV files found to migrate")
            return False
        
        # Get current database stats
        stats_before = db_manager.get_database_stats()
        logger.info("📊 Database stats before migration:")
        logger.info(f"   👥 Employees: {stats_before.get('employees_count', 0)}")
        logger.info(f"   📋 Projects: {stats_before.get('projects_count', 0)}")
        
        # Migrate employees
        if employees_exists:
            logger.info("👥 Migrating employees data...")
            try:
                employees_df = pd.read_csv(employees_csv_path)
                logger.info(f"📋 Loaded {len(employees_df)} employee records from CSV")
                
                # Clean data
                employees_df = clean_employees_data(employees_df)
                
                # Insert into database
                count = db_manager.bulk_insert_employees(employees_df)
                logger.info(f"✅ Migrated {count} employees to database")
                
            except Exception as e:
                logger.error(f"❌ Error migrating employees: {e}")
                return False
        
        # Migrate projects
        if projects_exists:
            logger.info("📋 Migrating projects data...")
            try:
                projects_df = pd.read_csv(projects_csv_path)
                logger.info(f"📋 Loaded {len(projects_df)} project records from CSV")
                
                # Clean data
                projects_df = clean_projects_data(projects_df)
                
                # Insert into database
                count = db_manager.bulk_insert_projects(projects_df)
                logger.info(f"✅ Migrated {count} projects to database")
                
            except Exception as e:
                logger.error(f"❌ Error migrating projects: {e}")
                return False
        
        # Get final database stats
        stats_after = db_manager.get_database_stats()
        logger.info("📊 Database stats after migration:")
        logger.info(f"   👥 Employees: {stats_after.get('employees_count', 0)}")
        logger.info(f"   📋 Projects: {stats_after.get('projects_count', 0)}")
        logger.info(f"   🎯 Skills: {stats_after.get('skills_count', 0)}")
        logger.info(f"   📝 Requirements: {stats_after.get('requirements_count', 0)}")
        
        # Calculate migration summary
        employees_added = stats_after.get('employees_count', 0) - stats_before.get('employees_count', 0)
        projects_added = stats_after.get('projects_count', 0) - stats_before.get('projects_count', 0)
        
        logger.info("📈 Migration Summary:")
        logger.info(f"   ➕ Employees added: {employees_added}")
        logger.info(f"   ➕ Projects added: {projects_added}")
        
        logger.info("🎉 CSV to Database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
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
    text_columns = ['Emp ID', 'Name', 'Skills', 'Role', 'Previous Project Description', 'Proficiency', 'Location']
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

def backup_csv_files():
    """Create backup of CSV files before migration"""
    try:
        logger.info("💾 Creating backup of CSV files...")
        
        backup_dir = 'datasets/backup'
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup employees CSV
        employees_csv_path = 'datasets/Employees.csv'
        if os.path.exists(employees_csv_path):
            backup_path = f'{backup_dir}/Employees_backup_{timestamp}.csv'
            import shutil
            shutil.copy2(employees_csv_path, backup_path)
            logger.info(f"✅ Backed up employees CSV to: {backup_path}")
        
        # Backup projects CSV
        projects_csv_path = 'datasets/Projects.csv'
        if os.path.exists(projects_csv_path):
            backup_path = f'{backup_dir}/Projects_backup_{timestamp}.csv'
            import shutil
            shutil.copy2(projects_csv_path, backup_path)
            logger.info(f"✅ Backed up projects CSV to: {backup_path}")
        
        logger.info("💾 Backup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return False

def verify_migration():
    """Verify that migration was successful"""
    try:
        logger.info("🔍 Verifying migration...")
        
        db_manager = DatabaseManager()
        
        # Get database stats
        stats = db_manager.get_database_stats()
        
        # Check if data exists
        if stats.get('employees_count', 0) == 0 and stats.get('projects_count', 0) == 0:
            logger.error("❌ No data found in database after migration")
            return False
        
        # Test data retrieval
        employees_df = db_manager.get_all_employees()
        projects_df = db_manager.get_all_projects()
        
        if employees_df.empty and projects_df.empty:
            logger.error("❌ Unable to retrieve data from database")
            return False
        
        logger.info("✅ Migration verification successful!")
        logger.info(f"   👥 Retrieved {len(employees_df)} employees")
        logger.info(f"   📋 Retrieved {len(projects_df)} projects")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🔄 AI-Driven Talent Management System - Data Migration")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'migrate':
            # Create backup first
            if backup_csv_files():
                success = migrate_csv_to_database()
                if success:
                    verify_migration()
        elif command == 'backup':
            success = backup_csv_files()
        elif command == 'verify':
            success = verify_migration()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: migrate, backup, verify")
            success = False
    else:
        # Default: migrate with backup
        print("🔄 Starting migration process...")
        if backup_csv_files():
            success = migrate_csv_to_database()
            if success:
                verify_migration()
        else:
            success = False
    
    if success:
        print("🎉 Migration process completed successfully!")
        print("💡 You can now use the application with database storage")
    else:
        print("❌ Migration process failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
