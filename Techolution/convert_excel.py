import pandas as pd
import os

def convert_excel_to_csv():
    """Convert Excel files to CSV format"""
    try:
        # Convert Employees.xlsx to CSV
        employees_df = pd.read_excel('datasets/Employees.csv.xlsx')
        employees_df.to_csv('datasets/Employees.csv', index=False)
        print("Converted Employees.xlsx to CSV")
        print("Employees columns:", employees_df.columns.tolist())
        print("Sample data:")
        print(employees_df.head())
        
        # Convert Projects.xlsx to CSV
        projects_df = pd.read_excel('datasets/Projects.csv.xlsx')
        projects_df.to_csv('datasets/Projects.csv', index=False)
        print("\nConverted Projects.xlsx to CSV")
        print("Projects columns:", projects_df.columns.tolist())
        print("Sample data:")
        print(projects_df.head())
        
    except Exception as e:
        print(f"Error converting files: {e}")

if __name__ == "__main__":
    convert_excel_to_csv()
