# College Recommendation System - Enhanced Version 2.0

A Flask-based web application that provides personalized college recommendations based on MHT-CET percentiles. Now with **PDF report generation** and **automated email delivery**!

## 🎯 Features

### Previous Version (v1.0)
- ✓ Student form submission
- ✓ College recommendation algorithm
- ✓ MongoDB database integration
- ✓ Admin panel for managing college information
- ✓ College chatbot

### New in Version 2.1 - User Authentication & Enhanced Features
- 🔐 **User Authentication System** - Register, login, and manage user accounts
- 👤 **Personal Dashboard** - View recent searches, favorite colleges, and activity summary
- ❤️ **Favorites System** - Save and manage favorite colleges
- 🔍 **College Comparison Tool** - Compare colleges side-by-side with detailed metrics
- 📊 **Search History Tracking** - Track and view previous college searches
- 🛡️ **Protected Routes** - Secure access to personalized features

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup wizard
python setup.py
```

### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env file:**
   ```bash
   cp .env.example .env
   # Edit .env with your email credentials
   ```

3. **Ensure MongoDB is running:**
   ```bash
   mongod
   ```

4. **Initialize database:**
   ```bash
   python db_init.py
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open in browser:**
   ```
   http://localhost:5000
   ```

## 📧 Email Setup

### Gmail (Recommended)
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or your device)
3. Copy the 16-character password
4. Paste in `.env` file under `MAIL_PASSWORD`

### Other Email Providers
- **Outlook**: smtp.outlook.com:587
- **Office365**: smtp.office365.com:587
- **Custom SMTP**: Update MAIL_SERVER and MAIL_PORT in .env

## 📋 Project Structure

```
college_recommendation_chatbot/
├── 📄 Core Application
│   ├── app.py                    # Main Flask application
│   ├── mongo_db.py              # MongoDB configuration
│   ├── recommender.py           # College recommendation engine
│   ├── chatbot_logic.py         # Chatbot response logic
│   ├── email_service.py         # Email sending module
│   └── report_generator.py      # PDF report generation
│
├── 🗂️ Database & Setup
│   ├── db_init.py               # Database initialization
│   ├── setup.py                 # Setup wizard
│   ├── cutoffs.csv              # Initial college data
│   └── requirements.txt          # Python dependencies
│
├── 🎨 Templates
│   ├── base.html                # Base template
│   ├── index.html               # Home page
│   ├── colleges.html            # Results page (UPDATED)
│   ├── chatbot.html             # Chatbot interface
│   ├── college_details.html     # College information
│   └── error.html               # Error page (NEW)
│
├── 🎯 Configuration
│   ├── .env.example             # Email config template
│   ├── SETUP.md                 # Detailed setup guide
│   └── README.md                # This file
│
└── 📦 Reports & Static
    ├── reports/                 # Generated PDF reports
    ├── static/                  # CSS and JavaScript
    └── __pycache__/            # Python cache

```

## 🔄 How It Works

### Student Flow
1. **Submit Form** → Student enters percentile, category, branch, city
2. **Get Recommendations** → System queries MongoDB for matching colleges
3. **View Results** → Colleges displayed with admission chances
4. **Generate Report** → Click "Generate & Email Report" button
5. **Receive Email** → Professional PDF sent to student's email

### Data Flow
```
CSV File → db_init.py → MongoDB (colleges_col)
                          ↓
                    recommender.py
                          ↓
                      app.py
                     ↙        ↘
            HTML Template    email_service.py
                     ↘        ↙
                  Student Email
```

## 🧪 Testing the Application

### Test with Sample Data
```bash
# The cutoffs.csv already contains 190+ college records
python db_init.py
```

### Test Email Configuration
```python
# In Python console:
from email_service import send_welcome_email
send_welcome_email("your-email@gmail.com", "Test User")
```

### Test Report Generation
```python
# In Python console:
from report_generator import generate_recommendation_report

student_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'percentile': 95.5,
    'category': 'OPEN',
    'branch': 'Computer Engineering',
    'city': 'Mumbai'
}

colleges = [
    {
        'college': 'VJTI',
        'branch': 'Computer Engineering',
        'category': 'OPEN',
        'cutoff': 99.2,
        'city': 'Mumbai',
        'chance': 'High'
    }
]

generate_recommendation_report(**student_data, colleges_list=colleges, output_path='test_report.pdf')
```

## 📝 Database Schema

### colleges collection
```javascript
{
  "_id": ObjectId,
  "college": "VJTI",
  "branch": "Computer Engineering",
  "category": "OPEN",
  "cutoff_percentile": 99.2,
  "city": "mumbai"
}
```

### students collection
```javascript
{
  "_id": ObjectId,
  "name": "John Doe",
  "email": "john@example.com",
  "percentile": 95.5,
  "category": "OPEN",
  "branch": "Computer Engineering",
  "city": "Mumbai",
  "timestamp": ISODate,
  "report_generated": true,
  "report_sent_at": ISODate,
  "report_path": "reports/..."
}
```

### intents collection
```javascript
{
  "_id": ObjectId,
  "college": "VJTI",
  "pattern": "fees",
  "response": "Annual fees are ₹1,20,000",
  "created_at": ISODate
}
```

## 🛠️ Configuration Options

### Email Configuration (.env)
```env
MAIL_SERVER=smtp.gmail.com          # SMTP server address
MAIL_PORT=587                        # SMTP port
MAIL_USE_TLS=True                    # Use TLS encryption
MAIL_USERNAME=your-email@gmail.com   # Your email address
MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx    # App password (16 chars)
MAIL_DEFAULT_SENDER=your-email@gmail.com  # Sender address
```

### Customization Points

**PDF Report Template** - Edit `report_generator.py`:
- Colors, fonts, layout
- Content sections and order
- Logo/branding

**Email Templates** - Edit `email_service.py`:
- Subject lines
- Email body content
- Attachment formatting

**Recommendation Algorithm** - Edit `recommender.py`:
- Matching criteria
- Cutoff tolerance thresholds
- Sorting preferences

## 🐛 Troubleshooting

### Email Not Sending?
```
❌ "Error sending email"
✓ Check .env file has correct credentials
✓ Verify App Password is 16 characters
✓ Check internet connection
✓ Try a different email provider in .env
```

### No College Data?
```
❌ "No colleges found"
✓ Run: python db_init.py
✓ Check cutoffs.csv exists
✓ Verify MongoDB is running: mongod
```

### MongoDB Connection Failed?
```
❌ "Error reading from MongoDB"
✓ Start MongoDB: mongod (Windows/Mac/Linux)
✓ Check connection string in mongo_db.py
✓ Default: mongodb://localhost:27017
```

### Session Expired Error?
```
❌ "Session expired. Please submit the form again"
✓ Reload the page
✓ Fill in the form again
✓ Generate report immediately
```

## 📊 API Reference

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/` | GET | Home page | HTML |
| `/features` | GET | Features showcase | HTML |
| `/recommend` | POST | Submit form & get recommendations | HTML with colleges |
| `/generate-report` | POST | Generate & email PDF report | JSON {success, message} |
| `/college/<name>` | GET | View college details | HTML |
| `/chatbot/<college>` | GET/POST | College chatbot interface | HTML |
| `/admin` | GET/POST | Admin panel for intents | HTML |

## 🔐 Security Considerations

- **Email credentials**: Stored in .env, not in code
- **MongoDB**: Default local connection (secure on local network)
- **Session secrets**: Should be changed in production
- **Report files**: Stored in local `reports/` directory

## 📈 Performance Features

- **MongoDB indexing**: Optimized queries for fast recommendations
- **PDF generation**: Memory-efficient report creation
- **Email queue**: Asynchronous email sending (can be enhanced)
- **Caching**: Session-based data storage

## 🚀 Future Enhancements

- [ ] Asynchronous email sending with Celery
- [ ] User authentication and login
- [ ] College comparison tool
- [ ] Mobile app version
- [ ] Real-time notification system
- [ ] Analytics dashboard
- [ ] API for third-party integration
- [ ] Multi-language support
- [ ] Advanced filtering UI
- [ ] Payment integration

## 📞 Support & Troubleshooting

1. **Check logs** - Look for errors in terminal output
2. **Read SETUP.md** - Detailed step-by-step guide
3. **Test MongoDB** - Run `mongo` command to verify connection
4. **Verify email** - Test with `python setup.py`
5. **Check file permissions** - Ensure `reports/` directory is writable

## 📜 License

This project is open source and available for educational purposes.

## 👨‍💻 Technologies Used

- **Backend**: Python, Flask
- **Database**: MongoDB
- **Email**: SMTP, python-email
- **Reports**: ReportLab (PDF generation)
- **Frontend**: HTML, CSS, Bootstrap
- **Hosting Ready**: Can be deployed to Heroku, AWS, Azure

## 📫 Contact & Feedback

For issues, suggestions, or contributions, please reach out!

---

**Version**: 2.0 (Enhanced with Reports & Email)
**Last Updated**: February 2026
**Status**: Production Ready ✅

### What's New in v2.0?
- ✨ MongoDB college data (dynamic updates)
- 📄 PDF report generation (professional format)
- 💌 Automated email delivery (SMTP integration)
- 🔄 Better error handling (user-friendly messages)
- ⚙️ Setup wizard (automated configuration)
- 📊 Enhanced database schema (improved structure)
