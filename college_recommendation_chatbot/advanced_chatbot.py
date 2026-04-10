"""
Advanced Interactive College Chatbot
Real-time verification from college websites with source citations
"""

from mongo_db import college_details_col
from web_scraper import WebScraper, DataVerifier
import re
from typing import Dict, List, Tuple

class AdvancedCollegeChatbot:
    """Enhanced chatbot with real-time verification and interactivity"""
    
    def __init__(self):
        self.conversation_history = []
        self.verification_cache = {}
    
    def ask_followup(self, response: Dict) -> str:
        """Generate follow-up questions"""
        college = response.get('college', '')
        question_type = response.get('type', '')
        
        followups = {
            'fees': [
                f"Would you like to know about hostel fees at {college}?",
                f"Are you interested in different payment plans for {college}?",
                "Would you like a comparison with other colleges?"
            ],
            'placement': [
                f"Interested in specific branches' placements at {college}?",
                "Would you like information about top recruiters?",
                f"Want to know about salary ranges for different roles?"
            ],
            'cutoff': [
                f"Do you know your JEE/MHT-CET percentile?",
                "Would you like information about other colleges in your range?",
                "Interested in category-wise cutoffs?"
            ],
            'hostel': [
                f"Would you like to know about nearby private accommodations?",
                "Are you interested in hostel mess charges breakdown?",
                f"Want to compare {college} hostel with others?"
            ]
        }
        
        if question_type in followups:
            import random
            return random.choice(followups[question_type])
        return "Would you like more information about this college?"
    
    def format_response_with_sources(self, data: Dict, college: str) -> str:
        """Format response with source citations"""
        response = f"\n📍 **Information for {college}**\n"
        response += "="*50 + "\n\n"
        
        if 'error' in data:
            response += f"⚠️ {data['error']}\n"
            return response
        
        if 'results' in data and data['results']:
            response += f"Found {len(data['results'])} relevant sources:\n\n"
            
            for idx, result in enumerate(data['results'], 1):
                response += f"**Source {idx}:** {result.get('title', 'N/A')}\n"
                response += f"📌 {result.get('snippet', 'N/A')[:150]}...\n"
                response += f"🔗 Link: {result.get('url', 'N/A')}\n\n"
        
        return response
    
    def answer_with_verification(
        self,
        user_input: str,
        college_name: str,
        branch_name: str = "",
        category: str = "OPEN"
    ) -> Dict:
        """
        Answer questions with real-time verification from websites
        
        Returns:
            {
                'answer': str,
                'sources': [],
                'verified': bool,
                'type': str (fees/placement/cutoff/hostel),
                'college': str,
                'followup': str
            }
        """
        
        user_input_lower = user_input.lower()
        response = {
            'college': college_name,
            'user_question': user_input,
            'sources': [],
            'verified': False,
            'followup': ''
        }
        
        # 1. Fetch official website and database information
        college_doc = college_details_col.find_one({
            "college": {"$regex": college_name, "$options": "i"}
        })
        
        scrape_data = WebScraper.scrape_college_site(college_name)
        official_description = ''
        official_news = []
        official_url = ''
        if isinstance(scrape_data, dict) and 'error' not in scrape_data:
            official_description = scrape_data.get('description', '')
            official_news = scrape_data.get('news', [])
            official_url = scrape_data.get('url', '')

        def format_source_lines(source_list):
            lines = []
            for idx, source in enumerate(source_list[:3], 1):
                title = source.get('title', 'Untitled Source')
                snippet = source.get('snippet', '').strip()
                url = source.get('url', '')
                lines.append(f"{idx}. {title}\n   {snippet[:140]}...\n   {url}")
            return "\n".join(lines)

        if not college_doc and not official_description:
            response['answer'] = f"Sorry, I don't have data for {college_name} in the system. Let me search online..."

        # FEES QUERY
        if any(word in user_input_lower for word in ["fee", "cost", "price", "expense", "tuition"]):
            response['type'] = 'fees'
            
            web_data = WebScraper.fetch_fees_info(college_name)
            response['sources'] = web_data.get('results', [])
            response['verified'] = bool(response['sources'])
            
            local_fees = college_doc.get('fees_per_year', 'N/A') if college_doc else 'N/A'
            local_hostel = college_doc.get('hostel_fee', 'N/A') if college_doc else 'N/A'
            
            answer = f"""
💰 Fees Information for {college_name}

"""
            if response['sources']:
                answer += "Latest information from current web sources:\n"
                answer += format_source_lines(response['sources'])
                answer += "\n\n"
            elif official_description:
                answer += f"Official site summary: {official_description}\n\n"
            else:
                answer += "Sorry, I couldn't find current fees information online. Please check the college's official website directly.\n"
            
            if official_url:
                answer += f"\nOfficial website: {official_url}\n"
            
            response['answer'] = answer
        
        # PLACEMENT QUERY
        elif any(word in user_input_lower for word in ["placement", "salary", "package", "job", "companies"]):
            response['type'] = 'placement'
            
            web_data = WebScraper.fetch_placement_info(college_name)
            response['sources'] = web_data.get('results', [])
            response['verified'] = bool(response['sources'])
            
            avg_pkg = college_doc.get('avg_package', 'N/A') if college_doc else 'N/A'
            placement_rate = college_doc.get('placement_rate', 'N/A') if college_doc else 'N/A'
            companies = college_doc.get('companies_hiring', []) if college_doc else []
            companies_str = ", ".join(companies[:5]) if companies else "Top companies recruiting currently."
            
            answer = f"""
💼 Placement Information for {college_name}

"""
            if response['sources']:
                answer += "Latest placement reports from web sources:\n"
                answer += format_source_lines(response['sources'])
                answer += "\n\n"
            elif official_description:
                answer += f"Official site summary: {official_description}\n\n"
            else:
                answer += "Sorry, I couldn't find current placement information online. Please check the college's official website directly.\n"
            
            if official_url:
                answer += f"\nOfficial website: {official_url}\n"
            
            response['answer'] = answer
        
        # CUTOFF QUERY
        elif any(word in user_input_lower for word in ["cutoff", "percentile", "admission", "eligible"]):
            response['type'] = 'cutoff'
            
            web_data = WebScraper.fetch_cutoff_info(college_name)
            response['sources'] = web_data.get('results', [])
            response['verified'] = bool(response['sources'])
            
            cutoff_current = college_doc.get('cutoff_percentile', 'N/A') if college_doc else 'N/A'
            cutoff_2023 = college_doc.get('cutoff_2023', 'N/A') if college_doc else 'N/A'
            cutoff_2024 = college_doc.get('cutoff_2024', 'N/A') if college_doc else 'N/A'
            
            answer = f"""
📈 Cutoff Information for {college_name}

"""
            if response['sources']:
                answer += "Latest cutoff insights from web sources:\n"
                answer += format_source_lines(response['sources'])
                answer += "\n\n"
            elif official_description:
                answer += f"Official site summary: {official_description}\n\n"
            else:
                answer += "Sorry, I couldn't find current cutoff information online. Please check the college's official website directly.\n"
            
            if official_url:
                answer += f"\nOfficial website: {official_url}\n"
            
            response['answer'] = answer
        
        # HOSTEL QUERY
        elif any(word in user_input_lower for word in ["hostel", "accommodation", "dorm", "stay", "lodge"]):
            response['type'] = 'hostel'
            
            web_data = WebScraper.fetch_hostel_info(college_name)
            response['sources'] = web_data.get('results', [])
            response['verified'] = bool(response['sources'])
            
            hostel_avail = college_doc.get('hostel_available', False) if college_doc else False
            hostel_fee = college_doc.get('hostel_fee', 'N/A') if college_doc else 'N/A'
            status_text = "Available ✓" if hostel_avail else "Limited/External"
            
            answer = f"""
🏠 Hostel Information for {college_name}

"""
            if response['sources']:
                answer += "Latest hostel and accommodation details from web sources:\n"
                answer += format_source_lines(response['sources'])
                answer += "\n\n"
            elif official_description:
                answer += f"Official site summary: {official_description}\n\n"
            else:
                answer += "Sorry, I couldn't find current hostel information online. Please check the college's official website directly.\n"
            
            if official_url:
                answer += f"\nOfficial website: {official_url}\n"
            
            response['answer'] = answer
        
        else:
            response['type'] = 'general'
            if official_description:
                general_info = official_description
            else:
                general_info = "I am fetching the latest information from the college website and recent sources."
            
            answer = f"""
ℹ️ General Information for {college_name}

{general_info}

You can ask about:
• Fees
• Placements
• Cutoff
• Hostel
• Courses
"""
            if official_url:
                answer += f"\nOfficial website: {official_url}\n"
            response['answer'] = answer
        
        # Add follow-up question
        response['followup'] = self.ask_followup(response)
        
        return response


def test_advanced_chatbot():
    """Test advanced chatbot"""
    print("\n🤖 Testing Advanced College Chatbot\n")
    
    chatbot = AdvancedCollegeChatbot()
    
    # Test queries
    test_queries = [
        ("What are the fees for SPIT?", "SPIT"),
        ("Tell me about VJTI placements", "VJTI"),
        ("What's the cutoff for COEP?", "COEP"),
        ("Do they have hostels?", "DY Patil")
    ]
    
    for question, college in test_queries:
        print(f"\n❓ Question: {question}")
        print(f"🎓 College: {college}")
        print("-" * 50)
        
        response = chatbot.answer_with_verification(question, college)
        
        print(f"✅ Answer:\n{response['answer']}")
        print(f"\n💡 Follow-up: {response['followup']}")
        print(f"🔗 Sources found: {len(response['sources'])}")
        print("\n" + "="*50)


if __name__ == "__main__":
    test_advanced_chatbot()
