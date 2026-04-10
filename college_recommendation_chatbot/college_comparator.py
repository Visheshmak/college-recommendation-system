from mongo_db import college_details_col
from web_scraper import WebScraper, DataVerifier
from typing import Dict, List
import json

class CollegeComparator:
    """Compare multiple colleges"""
    
    def __init__(self):
        self.colleges_data = {}
    
    def fetch_college_data(self, college_name: str) -> Dict:
        """Fetch all available data for a college"""
        try:
            data = college_details_col.find_one({
                "college": {"$regex": college_name, "$options": "i"}
            })
            
            if data:
                # Convert ObjectId to string
                data['_id'] = str(data['_id'])
            
            return data or {}
        except Exception as e:
            print(f"Error fetching college data: {e}")
            return {}
    
    def format_comparison_table(self, colleges: List[str], criteria: str) -> str:
        """
        Format comparison as HTML table
        
        Args:
            colleges: List of college names
            criteria: What to compare (fees/placement/cutoff/hostel)
        
        Returns:
            HTML table string
        """
        
        criteria_lower = criteria.lower()
        
        # Map criteria to database fields
        field_mapping = {
            'fees': 'fees_per_year',
            'placement': 'avg_package',
            'package': 'avg_package',
            'cutoff': 'cutoff_percentile',
            'hostel': 'hostel_fee',
            'companies': 'companies_hiring',
            'rate': 'placement_rate',
        }
        
        # Find relevant field
        field = None
        for key, db_field in field_mapping.items():
            if key in criteria_lower:
                field = db_field
                break
        
        if not field:
            return f"❌ Cannot compare on '{criteria}' - unsupported comparison type"
        
        # Fetch data for all colleges
        college_data_list = []
        for college in colleges:
            data = self.fetch_college_data(college)
            college_data_list.append({
                'name': college,
                'data': data,
                'value': data.get(field, 'N/A')
            })
        
        # Build HTML table
        html = f"""
<table style="width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px;">
    <thead>
        <tr style="background: #667eea; color: white;">
            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">College</th>
            <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">{criteria.title()}</th>
        </tr>
    </thead>
    <tbody>
"""
        
        for item in college_data_list:
            value = item['value']
            
            # Handle list values (like companies)
            if isinstance(value, list):
                value = ", ".join(value[:3])  # Show first 3
                if len(item['value']) > 3:
                    value += f" (+{len(item['value'])-3} more)"
            
            html += f"""        <tr style="border: 1px solid #ddd;">
            <td style="padding: 10px; font-weight: 600; background: #f5f5f5;">{item['name']}</td>
            <td style="padding: 10px; text-align: center; background: #fff;">{value}</td>
        </tr>
"""
        
        html += """    </tbody>
</table>
"""
        
        return html
    
    def compare_fees(self, colleges: List[str]) -> Dict:
        """Compare fees across colleges"""
        comparison = {
            'type': 'fees',
            'colleges': {},
            'cheapest': None,
            'most_expensive': None
        }
        
        for college in colleges:
            data = self.fetch_college_data(college)
            
            comparison['colleges'][college] = {
                'fees': data.get('fees_per_year', 'N/A'),
                'hostel': data.get('hostel_fee', 'N/A'),
                'city': data.get('city', 'N/A')
            }
        
        return comparison
    
    def compare_placements(self, colleges: List[str]) -> Dict:
        """Compare placement statistics"""
        comparison = {
            'type': 'placement',
            'colleges': {},
            'best_avg_package': None,
            'best_median_package': None
        }
        
        max_avg = 0
        max_median = 0
        
        for college in colleges:
            data = self.fetch_college_data(college)
            
            avg_pkg = data.get('avg_package', 'N/A')
            median_pkg = data.get('median_package', 'N/A')
            
            # Extract numeric values for comparison
            avg_value = float(avg_pkg.split()[0]) if isinstance(avg_pkg, str) and 'LPA' in avg_pkg else 0
            median_value = float(median_pkg.split()[0]) if isinstance(median_pkg, str) and 'LPA' in median_pkg else 0
            
            comparison['colleges'][college] = {
                'avg_package': avg_pkg,
                'median_package': median_pkg,
                'placement_rate': data.get('placement_rate', 'N/A'),
                'companies': data.get('companies_hiring', [])[:5]
            }
            
            if avg_value > max_avg:
                max_avg = avg_value
                comparison['best_avg_package'] = college
            
            if median_value > max_median:
                max_median = median_value
                comparison['best_median_package'] = college
        
        return comparison
    
    def compare_cutoffs(self, colleges: List[str]) -> Dict:
        """Compare admission cutoffs"""
        
        comparison = {
            'type': 'cutoff',
            'colleges': {},
            'highest_cutoff': None,
            'lowest_cutoff': None
        }
        
        max_cutoff = 0
        min_cutoff = 100
        
        for college in colleges:
            data = self.fetch_college_data(college)
            
            cutoff = data.get('cutoff_percentile', 'N/A')
            cutoff_value = float(cutoff) if isinstance(cutoff, (int, float)) else 0
            
            comparison['colleges'][college] = {
                'current_cutoff': cutoff,
                'cutoff_2024': data.get('cutoff_2024', 'N/A'),
                'cutoff_2023': data.get('cutoff_2023', 'N/A'),
                'category': data.get('category', 'OPEN')
            }
            
            if cutoff_value > max_cutoff:
                max_cutoff = cutoff_value
                comparison['highest_cutoff'] = college
            
            if cutoff_value < min_cutoff and cutoff_value > 0:
                min_cutoff = cutoff_value
                comparison['lowest_cutoff'] = college
        
        return comparison
    
    def get_best_college_for_criteria(self, colleges: List[str], criteria: str) -> Dict:
        """Get the best college for specific criteria"""
        
        criteria_lower = criteria.lower()
        
        if 'fee' in criteria_lower:
            comparison = self.compare_fees(colleges)
            # Find cheapest
            cheapest = min(
                comparison['colleges'].items(),
                key=lambda x: self._extract_numeric(x[1]['fees'])
            )
            return {
                'criteria': 'Lowest Fees',
                'winner': cheapest[0],
                'value': cheapest[1]['fees'],
                'comparison': comparison['colleges']
            }
        
        elif 'placement' in criteria_lower or 'package' in criteria_lower:
            comparison = self.compare_placements(colleges)
            return {
                'criteria': 'Best Average Package',
                'winner': comparison['best_avg_package'],
                'comparison': comparison['colleges']
            }
        
        elif 'cutoff' in criteria_lower:
            comparison = self.compare_cutoffs(colleges)
            return {
                'criteria': 'Lowest Admission Cutoff',
                'winner': comparison['lowest_cutoff'],
                'comparison': comparison['colleges']
            }
        
        return {'error': 'Unknown criteria'}
    
    @staticmethod
    def _extract_numeric(value) -> float:
        """Extract numeric value from string like '₹1,20,000'"""
        import re
        match = re.search(r'[\d,]+', str(value).replace(',', ''))
        return float(match.group()) if match else float('inf')
    
    def generate_comparison_report(self, colleges: List[str]) -> str:
        """Generate comprehensive comparison report"""
        
        report = f"\n📊 **Comparison Report: {', '.join(colleges)}**\n"
        report += "="*60 + "\n\n"
        
        # Fees comparison
        fees_comparison = self.compare_fees(colleges)
        report += "💰 **FEES COMPARISON**\n"
        for college, data in fees_comparison['colleges'].items():
            report += f"\n• {college}\n"
            report += f"  - Annual Fees: {data['fees']}\n"
            report += f"  - Hostel Fee: {data['hostel']}\n"
            report += f"  - Location: {data['city'].title()}\n"
        
        # Placement comparison
        report += "\n\n💼 **PLACEMENT COMPARISON**\n"
        placement_comparison = self.compare_placements(colleges)
        for college, data in placement_comparison['colleges'].items():
            report += f"\n• {college}\n"
            report += f"  - Average Package: {data['avg_package']}\n"
            report += f"  - Median Package: {data['median_package']}\n"
            report += f"  - Placement Rate: {data['placement_rate']}\n"
            report += f"  - Top Companies: {', '.join(data['companies'])}\n"
        
        # Cutoff comparison
        report += "\n\n📈 **CUTOFF COMPARISON**\n"
        cutoff_comparison = self.compare_cutoffs(colleges)
        for college, data in cutoff_comparison['colleges'].items():
            report += f"\n• {college}\n"
            report += f"  - Current: {data['current_cutoff']}\n"
            report += f"  - 2024: {data['cutoff_2024']}\n"
            report += f"  - 2023: {data['cutoff_2023']}\n"
            report += f"  - Category: {data['category']}\n"
        
        # Recommendations
        report += "\n\n⭐ **RECOMMENDATIONS**\n"
        
        # Best value (low fees, good placements)
        fees_comp = self.compare_fees(colleges)
        placement_comp = self.compare_placements(colleges)
        
        best_value = None
        for college in colleges:
            fees = self._extract_numeric(fees_comp['colleges'][college]['fees'])
            # Simple scoring (you can make this more sophisticated)
            if not best_value or fees < best_value[1]:
                best_value = (college, fees)
        
        if best_value:
            report += f"\n🏆 **Best Value**: {best_value[0]} (Lower fees)\n"
        
        if placement_comp['best_avg_package']:
            report += f"💼 **Best Placements**: {placement_comp['best_avg_package']}\n"
        
        if cutoff_comparison['lowest_cutoff']:
            report += f"📚 **Easiest Admission**: {cutoff_comparison['lowest_cutoff']}\n"
        
        return report


def test_comparator():
    """Test college comparator"""
    print("\n📊 Testing College Comparator\n")
    
    comparator = CollegeComparator()
    
    # Test comparison
    colleges = ['VJTI', 'COEP', 'SPIT']
    
    print("1. Fee Analysis:")
    fees = comparator.compare_fees(colleges)
    print(f"   Comparing: {colleges}")
    print(f"   Result: {str(fees)[:100]}...")
    
    print("\n2. Placement Analysis:")
    placements = comparator.compare_placements(colleges)
    print(f"   Best Average Package: {placements['best_avg_package']}")
    
    print("\n3. Full Comparison Report:")
    report = comparator.generate_comparison_report(colleges)
    print(report[:500] + "...")
    
    print("\n✅ Comparator tests completed!")


if __name__ == "__main__":
    test_comparator()
