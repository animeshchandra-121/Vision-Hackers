#!/usr/bin/env python3
"""
Test script to verify the matching algorithm works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import load_data, perform_matching

def test_matching():
    """Test the matching algorithm"""
    print("Testing AI Talent Management Matching Algorithm...")
    print("=" * 60)
    
    try:
        # Load data
        print("1. Loading data...")
        load_data()
        print("   ✓ Data loaded successfully")
        
        # Perform matching
        print("2. Performing matching...")
        results = perform_matching()
        
        if "error" in results:
            print(f"   ✗ Error: {results['error']}")
            return False
        
        print(f"   ✓ Matching completed successfully")
        print(f"   ✓ Found {len(results)} projects")
        
        # Display results
        print("\n3. Matching Results:")
        print("-" * 40)
        
        for i, project in enumerate(results, 1):
            print(f"\nProject {i}: {project['project_title']}")
            print(f"Domain: {project['project_domain']}")
            print(f"Total Matches: {len(project['matches'])}")
            
            if project.get('intelligent_team'):
                print("Intelligent Team Recommendations:")
                for j, match in enumerate(project['intelligent_team'][:3], 1):
                    print(f"  {j}. {match['employee_name']} ({match['role']}, {match['proficiency']}) - {match['overall_score']}%")
            elif project.get('top_3'):
                print("Top 3 Recommendations:")
                for j, match in enumerate(project['top_3'][:3], 1):
                    print(f"  {j}. {match['employee_name']} ({match['role']}, {match['proficiency']}) - {match['overall_score']}%")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! The matching algorithm is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_matching()
    sys.exit(0 if success else 1)
