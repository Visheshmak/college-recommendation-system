"""
Intelligent College Enquiry Chatbot
Answers questions about fees, placements, cutoffs, hostel, etc.
"""

from mongo_db import college_details_col
import re

def get_college_details(college_name, branch_name, category="OPEN"):
    """Fetch detailed info about a specific college"""
    try:
        # Search for college-branch-category combination
        college_doc = college_details_col.find_one({
            "college": {"$regex": college_name, "$options": "i"},
            "branch": {"$regex": branch_name, "$options": "i"},
            "category": category.upper()
        })
        
        # If not found, search just by college and category
        if not college_doc:
            college_doc = college_details_col.find_one({
                "college": {"$regex": college_name, "$options": "i"},
                "category": category.upper()
            })
        
        # If still not found, search just by college name
        if not college_doc:
            college_doc = college_details_col.find_one({
                "college": {"$regex": college_name, "$options": "i"}
            })
        
        return college_doc
    except Exception as e:
        print(f"Error fetching college details: {e}")
        return None


def answer_college_query(user_input, college_name, branch_name="", category="OPEN"):
    
    user_input_lower = user_input.lower()
    
    # Get college details from database
    college = get_college_details(college_name, branch_name, category)
    
    if not college:
        return f"Sorry, I couldn't find detailed information about {college_name}. Please check the college name and try again."
    
    # Extract college info
    college_name_full = college.get("college", "")
    branch_full = college.get("branch", "")
    fees = college.get("fees_per_year", "N/A")
    avg_pkg = college.get("avg_package", "N/A")
    median_pkg = college.get("median_package", "N/A")
    highest_pkg = college.get("highest_package", "N/A")
    placement_rate = college.get("placement_rate", "N/A")
    cutoff_current = college.get("cutoff_percentile", "N/A")
    cutoff_2023 = college.get("cutoff_2023", "N/A")
    cutoff_2024 = college.get("cutoff_2024", "N/A")
    companies = college.get("companies_hiring", [])
    hostel_avail = college.get("hostel_available", False)
    hostel_fee = college.get("hostel_fee", "N/A")
    city = college.get("city", "").title()
    
    # FEES QUERY
    if any(word in user_input_lower for word in ["fee", "cost", "price", "expense", "tuition"]):
        return f"""
📚 **Fees Information for {college_name_full} - {branch_full}**

Annual Fees: {fees}

💡 Other Costs:
• Hostel Fee: {hostel_fee} (if applicable)
• Books & Materials: ~₹5,000-10,000 per year
• Miscellaneous: ~₹3,000-5,000

📍 Location: {city}

Note: Fees may vary based on the category and updates from the college.
        """
    
    # PLACEMENTS QUERY
    elif any(word in user_input_lower for word in ["placement", "salary", "package", "job", "companies", "recruit", "hiring"]):
        companies_str = ", ".join(companies) if companies else "TCS, Infosys, Cognizant, and others"
        
        return f"""
💼 **Placement Statistics for {college_name_full} - {branch_full}**

🎯 Placement Rate: {placement_rate}
📊 Average Package: {avg_pkg}
🔝 Median Package: {median_pkg}
⭐ Highest Package: {highest_pkg}

🏢 **Top Companies Recruiting:**
{companies_str}

📈 **Placement Trends:**
• Graduate count: 80-120 per branch
• Companies visiting: 40-50+ in 2024
• Average interview rounds: 2-3

💼 Salary range typically between ₹5 LPA to ₹25+ LPA based on role and performance.
        """
    
    # HOSTELS QUERY
    elif any(word in user_input_lower for word in ["hostel", "accommodation", "dorm", "stay", "living", "lodge"]):
        hostel_status = "Available ✓" if hostel_avail else "Not Available"
        
        return f"""
🏠 **Hostel & Accommodation for {college_name_full}**

Hostel Status: {hostel_status}
Hostel Fee: {hostel_fee} per year

🛏️ **Hostel Facilities:**
• Separate boys and girls hostel
• WiFi connectivity
• 24/7 security
• Mess facilities (additional ₹5,000-8,000 per month)
• Common areas and recreational facilities

🔖 **Room Categories:**
• Single occupancy: Premium rooms
• 2-3 occupancy: Standard rooms
• Shared common spaces

📞 For hostel allocation, contact the college administration after admission.
        """
    
    # CUTOFF QUERY
    elif any(word in user_input_lower for word in ["cutoff", "percentile", "score", "merit", "admission"]):
        return f"""
📊 **Cutoff Percentiles for {college_name_full}**

**{branch_full} - {category} Category**

Current Year (2024): {cutoff_2024}
Previous Year (2023): {cutoff_2023}
Historical (2024): {cutoff_current}

📈 **Cutoff Trend:**
• Relatively stable over 2 years
• May vary ±2-3 percentile based on competition

✅ Eligibility:
Your percentile should be ≥ {cutoff_current} for secure admission in this category.
• {cutoff_current}+ = Safe Zone
• {cutoff_current - 2} to {cutoff_current} = Moderate Chance
• Below {cutoff_current} = Risky

⚠️ Cutoffs may vary by category (OPEN, OBC, SC, ST, VJNT).
        """
    
    # COURSE/ACADEMICS QUERY
    elif any(word in user_input_lower for word in ["course", "curriculum", "degree", "academic", "subject"]):
        return f"""
📚 **Academic Information for {college_name_full}**

**Program:** {branch_full}
**Duration:** 4 Years (Full-Time)
**Degree:** B.E. / B.Tech

📖 **Curriculum:**
• First Year: Core engineering fundamentals
• Second Year: Major specialization begins
• Third Year: Advanced topics & electives
• Fourth Year: Project & Hands-on learning

🔬 **Learning Resources:**
• Modern laboratories
• Industry-standard software
• Internship opportunities
• Research projects

🎓 Affiliation: University of Mumbai / SPPU (Pune) / GTDU

📞 For detailed curriculum, visit the college website or contact admissions.
        """
    
    # GENERAL INFO QUERY
    elif any(word in user_input_lower for word in ["info", "about", "general", "tell", "help", "campus"]):
        return f"""
ℹ️ **About {college_name_full}**

📍 **Location:** {city}
🎓 **Branch:** {branch_full}
🏫 **Category:** {category}

📊 **Key Stats:**
• Placement Rate: {placement_rate}
• Average Package: {avg_pkg}
• Highest Package: {highest_pkg}
• Current Cutoff: {cutoff_current} percentile

🏢 **Recruiting Companies:** {', '.join(companies[:5])} and more

🏠 **Hostel:** {hostel_status if hostel_avail else 'On-campus accommodation available'}

💰 **Annual Fees:** {fees}

🎯 **To Know More:**
Type specific questions about:
✓ Fees & Cost
✓ Placements & Salary
✓ Hostel & Accommodation
✓ Admission Cutoff
✓ Course & Academics
        """
    
    # DEFAULT RESPONSE
    else:
        return f"""
Hi! I'm here to help you with information about **{college_name_full} - {branch_full}**.

I can answer questions about:
✓ **Fees** - Annual costs and hostel charges
✓ **Placements** - Salary, companies, and placement rate
✓ **Cutoff** - Admission percentile requirements
✓ **Hostel** - Accommodation and facilities
✓ **Academics** - Course details and curriculum

Just ask me anything! For example:
- "What are the fees?"
- "What's the placement average salary?"
- "What's the cutoff percentile?"
- "Do you have hostel facilities?"
        """


# Example usage in the app would be:
# query_result = answer_college_query(
#     user_input="What's the placement package?",
#     college_name="VJTI",
#     branch_name="Computer Engineering",
#     category="OPEN"
# )
