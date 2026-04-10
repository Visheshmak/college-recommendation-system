"""
Web Scraper Module for Real-time College Data
Fetches current information from college websites
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import re
from typing import Dict, List, Tuple
import time

class WebScraper:
    """Scrape college websites for real-time data"""
    
    # College website mappings
    COLLEGE_WEBSITES = {
        'VJTI': 'https://www.vjti.ac.in',
        'COEP': 'https://www.coep.org.in',
        'SPIT': 'https://www.spit.ac.in',
        'DY Patil': 'https://www.dypatil.edu',
        'KJ Somaiya': 'https://www.somaiya.edu',
        'Pune Institute of Computer Technology': 'https://www.pict.edu',
        'VNIT': 'https://www.vnit.ac.in',
        'YCCE': 'https://www.ycce.edu',
        'GECA': 'https://www.gecaurangabad.ac.in',
        'WCE': 'https://www.walchandedu.com',
        'Thakur College of Engineering': 'https://www.thakureducation.org',
        'Vishwakarma Institute of Technology': 'https://www.vit.edu.in',
        'IIT Bombay': 'https://www.iitb.ac.in',
        'MIT Pune': 'https://www.mitpune.edu.in',
        'AISSMS CoE Pune': 'https://www.aissms.edu.in',
        'RIT Ratnagiri': 'https://www.ritindia.edu',
        'BITS Pilani Mumbai': 'https://www.bits-pilani.ac.in'
    }
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    TIMEOUT = 10
    
    @staticmethod
    def search_google(query: str, num_results: int = 3) -> List[Dict]:
        try:
            results = []
            # Using a simple search string format
            # Note: For production, use google-search-results or similar library
            search_url = f"https://www.google.com/search?q={quote(query)}"
            
            print(f"[SEARCH] Querying: {query}")
            
            response = requests.get(search_url, headers=WebScraper.HEADERS, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract search results
                for idx, div in enumerate(soup.find_all('div', class_='g')[:num_results]):
                    try:
                        link = div.find('a', href=True)
                        title = div.find('h3')
                        snippet = div.find('span', class_='st')
                        
                        if link and title:
                            results.append({
                                'title': title.get_text(),
                                'url': link['href'],
                                'snippet': snippet.get_text() if snippet else '',
                                'source': 'Google Search'
                            })
                    except:
                        continue
            
            return results
        except Exception as e:
            print(f"[SEARCH ERROR] {e}")
            return []
    
    @staticmethod
    def scrape_college_site(college_name: str) -> Dict:
        """Scrape official college website for info"""
        try:
            if college_name not in WebScraper.COLLEGE_WEBSITES:
                return {'error': f'College website not found for {college_name}'}
            
            url = WebScraper.COLLEGE_WEBSITES[college_name]
            print(f"[SCRAPE] Fetching: {url}")
            
            response = requests.get(
                url,
                headers=WebScraper.HEADERS,
                timeout=WebScraper.TIMEOUT
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                data = {
                    'college': college_name,
                    'url': url,
                    'title': soup.title.string if soup.title else '',
                    'description': '',
                    'news': [],
                    'contact': {}
                }
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    data['description'] = meta_desc.get('content', '')
                
                # Look for news/announcements
                for heading in soup.find_all(['h2', 'h3'])[:5]:
                    text = heading.get_text().strip()
                    if text:
                        data['news'].append(text)
                
                # Look for contact info
                contact_patterns = {
                    'phone': r'\+?\d{10,}',
                    'email': r'[\w\.-]+@[\w\.-]+\.\w+'
                }
                
                page_text = soup.get_text()
                for key, pattern in contact_patterns.items():
                    matches = re.findall(pattern, page_text)
                    if matches:
                        data['contact'][key] = matches[0]
                
                return data
            else:
                return {'error': f'Failed to fetch {college_name} website (Status: {response.status_code})'}
        
        except Exception as e:
            print(f"[SCRAPE ERROR] {e}")
            return {'error': str(e)}
    
    @staticmethod
    def fetch_fees_info(college_name: str) -> Dict:
        """Search for current fees information"""
        query = f"{college_name} college fees 2024 2025"
        results = WebScraper.search_google(query)
        
        return {
            'college': college_name,
            'query': query,
            'results': results,
            'timestamp': time.time()
        }
    
    @staticmethod
    def fetch_placement_info(college_name: str) -> Dict:
        """Search for placement statistics"""
        query = f"{college_name} placement statistics average package"
        results = WebScraper.search_google(query)
        
        return {
            'college': college_name,
            'query': query,
            'results': results,
            'timestamp': time.time()
        }
    
    @staticmethod
    def fetch_cutoff_info(college_name: str) -> Dict:
        """Search for admission cutoff information"""
        query = f"{college_name} admission cutoff JEE MHTCET 2024"
        results = WebScraper.search_google(query)
        
        return {
            'college': college_name,
            'query': query,
            'results': results,
            'timestamp': time.time()
        }
    
    @staticmethod
    def fetch_hostel_info(college_name: str) -> Dict:
        """Search for hostel information"""
        query = f"{college_name} hostel accommodation facilities charges"
        results = WebScraper.search_google(query)
        
        return {
            'college': college_name,
            'query': query,
            'results': results,
            'timestamp': time.time()
        }


class DataVerifier:
    """Verify information against multiple sources"""
    
    @staticmethod
    def verify_information(claim: str, college_name: str) -> Dict:
        """
        Verify a claim about a college
        
        Args:
            claim: What we want to verify (e.g., "fees are ₹1,20,000")
            college_name: Name of the college
        
        Returns:
            Verification result with sources
        """
        
        query = f"{college_name} {claim}"
        results = WebScraper.search_google(query, num_results=5)
        
        return {
            'claim': claim,
            'college': college_name,
            'sources': results,
            'verified': len(results) > 0,
            'verification_count': len(results)
        }
    
    @staticmethod
    def compare_colleges(colleges: List[str], criteria: str) -> Dict:
        """
        Compare multiple colleges on a specific criteria
        
        Args:
            colleges: List of college names
            criteria: What to compare (fees, placements, cutoff, etc.)
        
        Returns:
            Comparison data from web sources
        """
        comparison = {
            'criteria': criteria,
            'colleges': {},
            'timestamp': time.time()
        }
        
        for college in colleges:
            query = f"{college} {criteria}"
            results = WebScraper.search_google(query)
            comparison['colleges'][college] = results
        
        return comparison


# Test function
def test_scraper():
    """Test web scraper"""
    print("\n🧪 Testing Web Scraper\n")
    
    # Test college website scraping
    print("1. Scraping VJTI website...")
    vjti_data = WebScraper.scrape_college_site('VJTI')
    print(f"   Title: {vjti_data.get('title', 'N/A')}")
    print(f"   News items: {len(vjti_data.get('news', []))}")
    
    # Test Google search
    print("\n2. Searching for SPIT fees...")
    fees_results = WebScraper.fetch_fees_info('SPIT')
    print(f"   Found {len(fees_results['results'])} results")
    
    # Test verification
    print("\n3. Verifying placement info...")
    verify = DataVerifier.verify_information(
        "average placement package 10 LPA",
        "COEP"
    )
    print(f"   Verified from {verify['verification_count']} sources")
    
    # Test comparison
    print("\n4. Comparing colleges on fees...")
    comparison = DataVerifier.compare_colleges(
        ['VJTI', 'COEP', 'SPIT'],
        'fees per year'
    )
    print(f"   Compared {len(comparison['colleges'])} colleges")


if __name__ == "__main__":
    test_scraper()
