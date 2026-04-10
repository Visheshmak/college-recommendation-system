# Advanced Chatbot - Visual Guide & Flow Diagrams

## 🎯 How It All Works Together

### Data Flow Diagram

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│        Student Asks Question via Web Interface        │
│             "What are the fees for SPIT?"             │
│                                                        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  advanced_chatbot.html               │
        │  (Interactive Chat UI)               │
        │                                      │
        │  - College Selection                 │
        │  - Question Input                    │
        │  - Real-time Display                 │
        │  - Source View                       │
        └──────────────┬───────────────────────┘
                       │
                       ▼ (POST /advanced-college-enquiry)
        ┌──────────────────────────────────────┐
        │  app.py - Flask Route Handler        │
        │                                      │
        │  Receives: college, question         │
        └──────────────┬───────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │  AdvancedCollegeChatbot              │
        │  (Chatbot Logic)                     │
        │                                      │
        │  1. Analyze question type            │
        │  2. Find relevant data sources       │
        │  3. Verify information               │
        │  4. Format response                  │
        └──────────┬──────────────┬────────────┘
                   │              │
        ┌──────────▼──┐  ┌────────▼─────────────┐
        │ Local Data  │  │  Web Data Collection │
        │ (MongoDB)   │  │                      │
        │             │  │  - WebScraper       │
        │ 46 College  │  │  - Search Google    │
        │ Records     │  │  - Verify Sources   │
        │             │  │  - Cache Results    │
        │ Latest:     │  │                      │
        │ • Fees      │  │ DataVerifier checks │
        │ • Placements│  │ multiple sources    │
        │ • Cutoffs   │  │ for accuracy        │
        │ • Hostels   │  │                      │
        └──────────┬──┘  └────────┬─────────────┘
                   │              │
                   └──────┬───────┘
                          │
                          ▼
        ┌──────────────────────────────────────┐
        │  Response Formatting                 │
        │                                      │
        │  Answer + Sources + Verification     │
        │  + Follow-up Questions               │
        └──────────────┬───────────────────────┘
                       │
                       ▼ (JSON Response)
        ┌──────────────────────────────────────┐
        │  advanced_chatbot.html               │
        │  Display Results                     │
        │                                      │
        │  ✓ Answer in chat bubble             │
        │  ✓ Source cards with links           │
        │  ✓ Verification status               │
        │  ✓ Follow-up suggestions             │
        └──────────────────────────────────────┘
```

---

## 🔄 Question Classification & Routing

```
Question: "What are the fees?"
              │
              ▼
     ┌─────────────────┐
     │ Analyze Keywords│
     │ (fee, cost,     │
     │  price, etc.)   │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Classify Type   │
     └────────┬────────┘
              │
    ┌─────────┼─────────┬─────────┬──────────┐
    │         │         │         │          │
    ▼         ▼         ▼         ▼          ▼
  FEES   PLACEMENT  CUTOFF   HOSTEL    OTHER
    │         │         │         │          │
    ▼         ▼         ▼         ▼          ▼
 Fetch    Fetch      Fetch     Fetch    General
 from     placement  admission  hostel   Response
 local &  records &  cutoffs &  info &
 web      web data   web data   web data

 Result: Verified answer + Sources + Follow-up
```


## 💾 Data Storage & Caching

```
MongoDB Collection: college_details
(46 pre-loaded records)

Each Record Contains:
{
  college: "SPIT",
  branch: "Computer Science",
  category: "OPEN",
  fees_per_year: "₹1,25,000",
  hostel_fee: "₹52,000",
  avg_package: "11.8 LPA",
  placement_rate: "93%",
  companies_hiring: [list],
  cutoff_percentile: 99.0,
  cutoff_2024: 99.0,
  cutoff_2023: 99.2
}

Web Scrape Cache (with timestamps):
{
  college: "SPIT",
  type: "fees",
  results: [...],
  timestamp: 1708870620
}
```

---

## 🌐 Web Data Collection Process

```
User asks about college:
        │
        ▼
┌─────────────────────────┐
│ Multiple Data Sources:  │
└────────┬────────┬──────┬┐
         │        │      ││
    ┌────▼──┐ ┌──▼──┐ ┌─▼───┐
    │College│ │Google│ │Local │
    │Website│ │Search│ │Cache │
    └────┬──┘ └──┬──┘ └─┬───┘
         │       │      │
         ▼       ▼      ▼
    Parse HTML  Extract   Retrieve
    Extract     Info from from DB
    Categories Results    
         │       │      │
         └───┬───┴──┬───┘
             │      │
             ▼      ▼
        ┌─────────────────┐
        │  Data Verifier  │
        │                 │
        │ Cross-check     │
        │ information     │
        │ across sources  │
        └────────┬────────┘
                 │
         ┌───────┴───────┐
         │               │
         ▼               ▼
    Verified ✓      Found in
    Multiple        Multiple
    Sources         Sources

    Return Sources + Data + Confidence
```

---

## 📱 User Interface Flow

```
┌────────────────────────────────────────────┐
│  Advanced College Chatbot Interface        │
├────────────────────────────────────────────┤
│                                            │
│  Header: "Advanced College Chatbot"        │
│  "Real-time information with live         │
│   web verification"                       │
│                                            │
├────────────────────────────────────────────┤
│  Chat Messages Area (Scrollable)          │
│  ┌────────────────────────────────────┐   │
│  │ Welcome message & instructions    │   │
│  │ ┌──────────────────────────────┐  │   │
│  │ │ User: What are the fees?     │  │   │
│  │ └──────────────────────────────┘  │   │
│  │ ┌──────────────────────────────┐  │   │
│  │ │ Bot: 📚 Fees Information     │  │   │
│  │ │                              │  │   │
│  │ │ ✓ Verified from 3 sources   │  │   │
│  │ │                              │  │   │
│  │ │ 📌 Sources:                  │  │   │
│  │ │ 1. Official Website          │  │   │
│  │ │    [Read more link]          │  │   │
│  │ │ 2. Education Portal          │  │   │
│  │ │    [Read more link]          │  │   │
│  │ │                              │  │   │
│  │ │ 💡 Follow-up:               │  │   │
│  │ │ "Interested in hostel fees?"│  │   │
│  │ └──────────────────────────────┘  │   │
│  └────────────────────────────────────┘   │
│                                            │
├────────────────────────────────────────────┤
│  Input Area:                               │
│  ┌───────────┐ ┌──────────────┐ ┌──────┐ │
│  │ College ▼ │ │ Your question│ │ Send │ │
│  │ [SPIT]    │ │              │ │      │ │
│  └───────────┘ └──────────────┘ └──────┘ │
│                                            │
│  Type: Shift+Enter for new line, Enter   │
│        to send                            │
│                                            │
└────────────────────────────────────────────┘
```

---

## 🎯 Supported Question Types & Responses

```
Question Type    Pattern Match         Data Source         Follow-up
──────────────────────────────────────────────────────────────────────

FEES            fee, cost, price,     Local DB +          "Want hostel
                expense, tuition       College website     fees info?"
                
PLACEMENT       placement, salary,    Placement records   "Bothered about
                package, companies     + Web search        salary range?"
                job, hiring, recruit   
                
CUTOFF          cutoff, percentile,   Admission portal    "Know your
                admission, eligible    + Official notices  percentile?"
                
HOSTEL          hostel, accommodation, College website     "Want private
                dorm, stay, lodge      + Facility info     options?"
                
GENERAL         Anything else         General response    "Ask about fees,
                                                          placements, etc?"

COMPARISON      compare, vs, better,  Multiple sources    "Which best for
                which, best, cheaper   + Analysis          your criteria?"


Response Format (Standard):
┌─────────────────────────────────────┐
│ 📚 **Title for [College]**          │
├─────────────────────────────────────┤
│ 📊 From Our Database:               │
│    Key Info: Value                  │
│                                     │
│ 🔗 Real-time Web Sources:           │
│    Source 1: Title & Link           │
│    Source 2: Title & Link           │
│                                     │
│ ✓ Information verified from X       │
│   sources                           │
│                                     │
│ 💡 Follow-up Suggestion             │
└─────────────────────────────────────┘
```

---

## 🔄 Comparison Feature Flow

```
User: "Compare VJTI, COEP, SPIT on fees"
       │
       ▼
   CollegeComparator
       │
       ├─ Fetch VJTI data from MongoDB
       ├─ Fetch COEP data from MongoDB
       ├─ Fetch SPIT data from MongoDB
       │
       ▼
   Extract Fees
       │
       ├─ VJTI: ₹1,20,000
       ├─ COEP: ₹1,15,000
       └─ SPIT: ₹1,25,000
       │
       ▼
   Format Table
       │
   ┌─────────────────────────────┐
   │ College | Annual Fees       │
   ├─────────────────────────────┤
   │ COEP    | ₹1,15,000 (Cheapest)│
   │ VJTI    | ₹1,20,000         │
   │ SPIT    | ₹1,25,000         │
   └─────────────────────────────┘
       │
       ▼
   Return Comparison + Recommendation
```

---

## 📊 Module Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    FLASK APP (app.py)                      │
│           Routes: /advanced-chatbot                        │
│                   /advanced-college-enquiry                │
│                                                             │
└────────────┬───────────────────────────────────────────────┘
             │
    ┌────────┴────────────────────────────────────┐
    │                                              │
    ▼                                              ▼
┌─────────────────────────────┐  ┌──────────────────────────┐
│  advanced_chatbot.py        │  │ college_comparator.py    │
│  (Response Generation)      │  │ (Comparison Logic)       │
│                             │  │                          │
│ AdvancedCollegeChatbot      │  │ CollegeComparator        │
│ - answer_with_verification │  │ - compare_fees()         │
│ - ask_followup()            │  │ - compare_placements()   │
│ - format_response()         │  │ - compare_cutoffs()      │
│ - response_decoration()     │  │ - generate_report()      │
└────────┬────────────────────┘  └──────────┬───────────────┘
         │                                   │
         └───────────────┬───────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────┐
         │  HTML/CSS/JS Templates           │
         │  advanced_chatbot.html           │
         │ (User Interface)                 │
         │                                  │
         │ Interactive Chat Display         │
         │ Source Citations                 │
         │ Follow-up Buttons                │
         │ Response Formatting              │
         └──────────────┬───────────────────┘
                        │
         ┌──────────────┴──────────────────┐
         │                                  │
         ▼                                  ▼
    ┌─────────────────────┐  ┌─────────────────────┐
    │  web_scraper.py     │  │  mongo_db.py        │
    │ (Data Collection)   │  │  (Data Storage)     │
    │                     │  │                     │
    │ WebScraper:         │  │ college_details_col │
    │ - search_google()   │  │ (46 pre-loaded)     │
    │ - scrape_site()     │  │                     │
    │ - fetch_info()      │  │ students_col        │
    │                     │  │ intents_col         │
    │ DataVerifier:       │  │                     │
    │ - verify_info()     │  │                     │
    │ - compare()         │  │                     │
    └─────────────┬───────┘  └──────────┬──────────┘
                  │                     │
                  │   ┌─────────────────┘
                  │   │
                  ▼   ▼
          External & Local Data Sources
          ├─ College Websites
          ├─ Google Search
          ├─ MongoDB Database
          └─ Cached Results
```

---

## ⚙️ Configuration & Settings

```
Environment (.env)
├─ WEB_SCRAPER_TIMEOUT = 10 seconds
├─ CACHE_ENABLED = true
├─ CACHE_TTL = 3600 seconds (1 hour)
├─ GOOGLE_SEARCH_RESULTS = 3
├─ VERIFY_SOURCES = true
└─ USE_LLM = false (optional)

Web Scraper Configuration (web_scraper.py)
├─ COLLEGE_WEBSITES = {mapping}
├─ HEADERS = {User-Agent}
├─ TIMEOUT = 10 seconds
└─ Retry logic on failure

Chatbot Configuration (advanced_chatbot.py)
├─ Response formatting rules
├─ Follow-up question templates
├─ Verification confidence levels
└─ Source citation format
```

---

## 🎓 Example Conversation Flow

```
┌─────────────────────────────────────┐
│  User Selects College: SPIT        │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  User Types: "What are the fees?"  │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Question Classified: TYPE_FEES    │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Fetch Data:                       │
│  ├─ Local: SPIT fees = ₹1,25,000  │
│  └─ Web: Google "SPIT fees 2024"  │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Verify from 3 sources             │
│  All confirm: ₹1,25,000            │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│  Format Response:                                  │
│  ┌─────────────────────────────────────────────┐  │
│  │ 📚 **Fees Information for SPIT**            │  │
│  │                                             │  │
│  │ Annual Fees: ₹1,25,000                     │  │
│  │ Hostel Fee: ₹52,000                        │  │
│  │                                             │  │
│  │ 🔗 **Real-time Web Sources:**              │  │
│  │ 1. SPIT Official Website                   │  │
│  │    Annual fees for SPIT are ₹1,25,000...  │  │
│  │    [🔗 Read more]                          │  │
│  │                                             │  │
│  │ 2. Educational Portal                      │  │
│  │    ...                                      │  │
│  │                                             │  │
│  │ ✓ Information verified from 3 sources     │  │
│  │                                             │  │
│  │ 💡 Would you like to know about           │  │
│  │    hostel fees at SPIT?                   │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Display in Chat Bubble            │
│  Show Follow-up Suggestion         │
│  Make Sources Clickable            │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  User Can:                         │
│  ├─ Click follow-up suggestion    │
│  ├─ Ask new question              │
│  ├─ Click source links            │
│  ├─ Switch to different college   │
│  └─ Scroll for more details       │
└─────────────────────────────────────┘
```

---

## 🚀 Deployment Architecture

```
Local Development:
┌──────────────────────────┐
│  Python Flask App (5000) │
│       ↓ ↑                │
│    MongoDB (27017)       │
│       ↓ ↑                │
│  Web Scraper (requests)  │
│       ↓ ↑                │
│   BeautifulSoup4 (parse) │
│       ↓ ↑                │
│   External Websites      │
│   Google Search API      │
└──────────────────────────┘

Production Ready:
┌──────────────────────────────────┐
│    Load Balancer (nginx)         │
│           ↓                       │
│ ┌─────────────────────────────┐  │
│ │  Multiple Flask Instances   │  │
│ │  (Scaled horizontally)      │  │
│ │           ↓                  │  │
│ │  MongoDB Replica Set        │  │
│ │  (High Availability)        │  │
│ │           ↓                  │  │
│ │  Cache Layer (Redis)        │  │
│ │  (Scraping Results)         │  │
│ └─────────────────────────────┘  │
└──────────────────────────────────┘
```

---

**Visual Guide Complete!** 📊

Use these diagrams to understand:
- Data flows
- Question routing
- UI interactions
- Module relationships
- Configuration options
- Comparison logic

---
