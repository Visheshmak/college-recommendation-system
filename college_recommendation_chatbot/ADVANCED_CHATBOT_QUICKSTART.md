# Advanced Chatbot - Quick Start Guide

## 🚀 Getting Started

### 1. Prerequisites
✅ MongoDB running  
✅ Python 3.8+  
✅ Virtual environment activated  
✅ All dependencies installed (including beautifulsoup4, lxml)

### 2. Start the Application

```bash
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Navigate to project directory
cd college_recommendation_chatbot

# 3. Make sure college data is loaded in MongoDB
python db_init.py

# 4. Start Flask app
python app.py

# 5. Open in browser
http://localhost:5000/advanced-chatbot
```

### 3. Using the Advanced Chatbot

#### Select College
Choose a college from the dropdown menu:
- VJTI
- COEP
- SPIT
- DY Patil
- IIT Bombay
- NIT

#### Ask Questions

Examples:
```
"What are the fees?"
"Tell me about placements"
"What's the cutoff for admission?"
"Do they have hostel facilities?"
```

#### Follow Real-time Verification
- **Green Check (✓)**: Information verified from multiple sources
- **Sources Panel**: Shows websites where info was found
- **Source Links**: Click to read original sources

#### Use Follow-up Questions
- Suggestions appear automatically
- Click them to ask related questions
- Chat maintains context

---

## 📋 Features Breakdown

### 1. Real-time Web Scraping
```python
from web_scraper import WebScraper

# Fetch fees information
fees = WebScraper.fetch_fees_info('SPIT')

# Scrape college website
college_data = WebScraper.scrape_college_site('VJTI')

# Search Google for updates
results = WebScraper.search_google('COEP placement 2024')
```

### 2. Data Verification
```python
from advanced_chatbot import AdvancedCollegeChatbot

chatbot = AdvancedCollegeChatbot()
response = chatbot.answer_with_verification(
    "What are the fees?",
    "SPIT"
)
# Returns: answer + sources + verification status
```

### 3. College Comparison
```python
from college_comparator import CollegeComparator

comparator = CollegeComparator()

# Compare fees
fees_comp = comparator.compare_fees(['VJTI', 'COEP', 'SPIT'])

# Compare placements
placements = comparator.compare_placements(['VJTI', 'COEP', 'SPIT'])

# Generate full report
report = comparator.generate_comparison_report(['VJTI', 'COEP', 'SPIT'])
```

---

## 🔧 API Endpoints

### Advanced Chatbot Interface
**GET** `/advanced-chatbot`
- Opens the interactive chatbot UI

### College Enquiry API
**POST** `/advanced-college-enquiry`

Request:
```json
{
  "college": "SPIT",
  "question": "What are the fees?"
}
```

Response:
```json
{
  "success": true,
  "college": "SPIT",
  "question": "What are the fees?",
  "answer": "📚 **Fees Information for SPIT**...",
  "verified": true,
  "sources": [
    {
      "title": "SPIT Official Website",
      "snippet": "Annual fees for SPIT...",
      "url": "https://..."
    }
  ],
  "sources_count": 3,
  "followup": "Would you like to know about hostel fees?",
  "type": "fees"
}
```

---

## 🎯 Common Questions

### Q: How does the chatbot get real-time data?
**A:** It uses two methods:
1. **Web Scraping**: Directly fetches from college websites
2. **Google Search**: Finds latest information and news

### Q: Is the data reliable?
**A:** Yes! Every answer is verified against multiple sources and sources are cited.

### Q: What if a source says something different?
**A:** The chatbot shows all sources so you can verify the information yourself.

### Q: Can I add more colleges?
**A:** Yes! Edit `COLLEGE_WEBSITES` in `web_scraper.py`:
```python
'Your College Name': 'https://official-website.com'
```

### Q: How often is data updated?
**A:** Real-time from web sources. Local database is used for caching.

---

## 📊 Understanding the Response

### Response Structure

```
📚 **Fees Information for SPIT**     ← College & Topic
========================

📊 From Our Database:               ← Cached Data
   Annual Fees: ₹1,25,000
   Hostel Fee: ₹52,000

🔗 **Real-time Web Sources:**        ← Live Verification
   1. SPIT Official Fee Structure
      Annual fees for SPIT are ₹1,25,000...
      🔗 Read more

✓ Information verified from 3 sources  ← Verification Status

💡 Would you like to know about hostel fees?  ← Follow-up
```

### Color Coding
- 🟢 **Green**: Verified from multiple sources
- 🟠 **Orange**: From cached database (older but reliable)
- 🔵 **Blue**: Sources and references
- 🟡 **Yellow**: Follow-up suggestions

---

## 🛠️ Troubleshooting

### Issue: "No sources found"
**Solution**: 
- Check internet connection
- Website might be temporarily unavailable
- Try a different search term

### Issue: No responses from chatbot
**Solution**:
- Ensure MongoDB is running
- Check Flask is running without errors
- Refresh the page

### Issue: Slow responses
**Solution**:
- Web scraping takes time (3-5 seconds typical)
- Check your internet speed
- Enable caching in settings

### Issue: Data seems outdated
**Solution**:
- Click "Refresh" to force new web search
- Local database might have cached data
- Official sources will have latest info

---

## 📈 Performance Tips

1. **Cache Enabled**: First query takes 3-5 seconds, subsequent queries use cache
2. **Search Optimization**: Use specific keywords for faster results
3. **Direct College Search**: College website scraping is faster than Google search
4. **Offline Mode**: Works with local MongoDB data even if web is unavailable

---

## 🔐 Privacy & Safety

✅ **What's Tracked**:
- Your questions (for improvement)
- College preferences (for recommendations)

❌ **What's NOT Tracked**:
- Personal information
- Email addresses
- Phone numbers

---

## 📞 Support

For issues or questions:
1. Check ADVANCED_CHATBOT.md for detailed documentation
2. Review error messages in browser console (F12)
3. Check Flask logs in terminal
4. Verify MongoDB is running

---

## 🎓 Example Use Cases

### Use Case 1: Comparing Colleges
```
Student: "What are the fees?"
Chatbot: Shows SPIT fees with sources
Student: (Clicks follow-up) "How about COEP?"
Chatbot: Shows COEP fees
Student: "Which is cheaper?"
Chatbot: COEP is ₹1,15,000 vs SPIT's ₹1,25,000
```

### Use Case 2: Placement Research
```
Student: "Tell me about placements"
Chatbot: Shows average package, placement rate, companies
Student: "Which companies hire?"
Chatbot: Lists top companies with live verification
Student: "What's the salary range?"
Chatbot: ₹5-25 LPA range with sources
```

### Use Case 3: Admission Planning
```
Student: "What's the JEE cutoff?"
Chatbot: Shows current and historical cutoffs
Student: "Is my percentile eligible?"
Chatbot: Compares student's percentile with cutoff
Student: "What about category?"
Chatbot: Shows category-wise cutoffs
```

---

## 🚀 Next Steps

1. **Explore all colleges**: Try different colleges to understand data
2. **Bookmark sources**: Save helpful sources for reference
3. **Cross-verify data**: Compare with official websites
4. **Plan admissions**: Use comparison data to make decisions

---

Happy Learning! 🎓
