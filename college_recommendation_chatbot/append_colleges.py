import csv
from maharashtra_colleges_scraper import COLLEGE_DATA

def append_to_csv():
    
    
    entries = []
    
    for college_name, branches_data in COLLEGE_DATA.items():
        for branch_data in branches_data:
            entry = {
                'college': college_name,
                'branch': branch_data.get('branch', ''),
                'category': branch_data.get('category', 'OPEN'),
                'cutoff_percentile': branch_data.get('cutoff_percentile', 0),
                'city': branch_data.get('city', ''),
                '2023_cutoff': branch_data.get('2023_cutoff', 0),
                '2024_cutoff': branch_data.get('2024_cutoff', 0),
                'fees_per_year': branch_data.get('fees_per_year', 'N/A'),
                'avg_package': branch_data.get('avg_package', 0),
                'placement_rate': branch_data.get('placement_rate', '0%'),
                'median_package': branch_data.get('median_package', '₹0 LPA'),
                'highest_package': branch_data.get('highest_package', '₹0 LPA'),
                'companies_hiring': branch_data.get('companies_hiring', ''),
                'hostel_available': 'Yes',
                'hostel_fee': '₹50,000 - ₹70,000'
            }
            entries.append(entry)
    
    # Append to CSV
    with open('colleges_details.csv', 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['college', 'branch', 'category', 'cutoff_percentile', 'city', '2023_cutoff', 
                     '2024_cutoff', 'fees_per_year', 'avg_package', 'placement_rate', 'median_package', 
                     'highest_package', 'companies_hiring', 'hostel_available', 'hostel_fee']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(entries)
    
    print(f"✓ Appended {len(entries)} new college records")
    print(f"✓ New colleges added: {len(set(e['college'] for e in entries))}")
    
    # List all unique colleges now
    colleges = set(e['college'] for e in entries)
    print("\nNew colleges added to database:")
    for c in sorted(colleges):
        print(f"  ✓ {c}")

if __name__ == '__main__':
    append_to_csv()
