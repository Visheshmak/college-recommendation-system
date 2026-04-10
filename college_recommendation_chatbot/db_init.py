"""
Database initialization script - Load college cutoff data from CSV to MongoDB
Run this script once to populate the colleges collection
"""

import csv
import os
from mongo_db import colleges_col, college_details_col

def load_colleges_from_csv(csv_path=None):
    """Load college cutoff data from CSV into MongoDB"""
    
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), 'cutoffs.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at {csv_path}")
        return False
    
    try:
        # Clear existing data (optional)
        colleges_col.delete_many({})
        
        # Read and insert data
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            colleges = []
            
            for row in reader:
                college_doc = {
                    'college': row['college'].strip(),
                    'branch': row['branch'].strip(),
                    'category': row['category'].strip().upper(),
                    'cutoff_percentile': float(row['cutoff_percentile']),
                    'city': row['city'].strip().lower(),
                    'exam_type': row.get('exam_type', 'MHT-CET').strip() if row.get('exam_type') else 'MHT-CET'
                }
                colleges.append(college_doc)
            
            if colleges:
                result = colleges_col.insert_many(colleges)
                print(f"✓ Successfully loaded {len(colleges)} college records into MongoDB")
                return True
            else:
                print("❌ No data found in CSV file")
                return False
                
    except Exception as e:
        print(f"❌ Error loading CSV data: {str(e)}")
        return False


def load_college_details_from_csv(csv_path=None):
    """Load detailed college data (fees, placements, 2-year cutoffs) from CSV"""
    
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), 'colleges_details.csv')
    
    if not os.path.exists(csv_path):
        print(f"⚠️  Detailed CSV file not found at {csv_path}")
        print("   This is optional - Continue with basic data only")
        return False
    
    try:
        # Clear existing detailed data
        college_details_col.delete_many({})
        
        # Read and insert detailed data
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            details = []
            
            for row in reader:
                detail_doc = {
                    'college': row['college'].strip(),
                    'branch': row['branch'].strip(),
                    'category': row['category'].strip().upper(),
                    'city': row['city'].strip().lower(),
                    'cutoff_percentile': float(row['cutoff_percentile']),
                    'exam_type': row.get('exam_type', 'MHT-CET').strip() if row.get('exam_type') else 'MHT-CET',
                    'cutoff_2023': float(row.get('2023_cutoff', row['cutoff_percentile'])),
                    'cutoff_2024': float(row.get('2024_cutoff', row['cutoff_percentile'])),
                    'fees_per_year': row['fees_per_year'].strip(),
                    'avg_package': row['avg_package'].strip(),
                    'placement_rate': row['placement_rate'].strip(),
                    'median_package': row['median_package'].strip(),
                    'highest_package': row['highest_package'].strip(),
                    'companies_hiring': [c.strip() for c in row['companies_hiring'].split(',')],
                    'hostel_available': row['hostel_available'].strip().lower() == 'yes',
                    'hostel_fee': row['hostel_fee'].strip(),
                }
                details.append(detail_doc)
            
            if details:
                result = college_details_col.insert_many(details)
                print(f"✓ Successfully loaded {len(details)} detailed college records into MongoDB")
                return True
            else:
                print("❌ No detailed data found in CSV file")
                return False
                
    except Exception as e:
        print(f"❌ Error loading detailed CSV data: {str(e)}")
        return False


def verify_college_data():
    """Verify that college data is loaded in MongoDB"""
    count = colleges_col.count_documents({})
    detail_count = college_details_col.count_documents({})
    
    print(f"\n📊 Database Statistics:")
    print(f"   Basic college records: {count}")
    print(f"   Detailed college records: {detail_count}")
    
    if count > 0:
        sample = colleges_col.find_one()
        print(f"\n📌 Sample basic record: {sample}")
    
    if detail_count > 0:
        detail_sample = college_details_col.find_one()
        print(f"\n📌 Sample detailed record:")
        for key, value in detail_sample.items():
            if key != '_id':
                print(f"   {key}: {value}")
    
    return count > 0


if __name__ == "__main__":
    print("=" * 60)
    print("Loading College Data to MongoDB")
    print("=" * 60)
    
    if load_colleges_from_csv():
        load_college_details_from_csv()
        print("\n" + "=" * 60)
        print("Verification:")
        verify_college_data()
    else:
        print("Failed to load college data")
