from flask import Flask, render_template, request, session, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from bson import ObjectId

# Load .env file FIRST, before any other imports
load_dotenv()

from recommender import recommend_colleges
from chatbot_logic import get_response
from college_chatbot import answer_college_query  # NEW: Import college chatbot
from advanced_chatbot import AdvancedCollegeChatbot  # NEW: Advanced interactive chatbot
from mongo_db import students_col, intents_col, college_details_col, search_logs_col, colleges_col, saved_colleges_col  # Added search logs collection
from report_generator import generate_report_with_details
from email_service import send_report_email, send_welcome_email
from api_routes import api_bp  # Import API blueprint
import tempfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = "student_secret_key"

# Register API blueprint
app.register_blueprint(api_bp)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Flask-WTF
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for simplicity in this demo

# Create reports directory
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.name = user_data.get('name', '')

@login_manager.user_loader
def load_user(user_id):
    from mongo_db import users_col
    user_data = users_col.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# WTForms for registration and login
class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])
    name = StringField('Full Name', [validators.DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField('Login')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/features")
def features():
    return render_template("features.html")


@app.route("/chatbot/demo", methods=["GET", "POST"])
def chatbot_demo():
    """Interactive chatbot demo - uses trained data from MongoDB"""
    reply = ""
    user_msg = ""

    if request.method == "POST":
        user_msg = request.form.get("message", "")

        if user_msg.strip():
            log_user_search("chatbot_demo", user_msg)

            # Fetch trained intents from MongoDB
            try:
                intents = list(intents_col.find(
                    {"type": "college_qa"},
                    {"pattern": 1, "response": 1, "category": 1}
                ))
                
                # If no trained intents, use sample ones
                if not intents:
                    intents = [
                        {"pattern": "fees", "response": "Fees vary by college. For example, fees typically range from ₹1,00,000 to ₹1,50,000 per year."},
                        {"pattern": "placements", "response": "Average placements are around 6-8 LPA, with top companies like TCS, Infosys, Google visiting."},
                        {"pattern": "hostel", "response": "Hostel facilities are available with fees around ₹40,000 to ₹60,000 per year, plus mess charges."},
                        {"pattern": "admission", "response": "Admission is based on MHT-CET percentile and category. Cutoff varies by college."}
                    ]
                
                reply = get_response(user_msg, intents)
                
            except Exception as e:
                print(f"Error fetching intents: {e}")
                reply = "Sorry, I encountered an error. Please try again."

    return render_template("chatbot_demo.html", reply=reply, user_msg=user_msg)


@app.route("/student-details")
def student_details():
    # Pre-fill form with previous data if available
    student_data = session.get('student_data', {})
    
    # Get unique cities from database
    try:
        cities = sorted(set(doc.get('city', '').title() for doc in colleges_col.find({}, {'city': 1}) if doc.get('city')))
    except:
        cities = []
    
    return render_template("student_details.html", student_data=student_data, cities=cities)


@app.route("/college/<college_name>")
def college_details(college_name):
    # Fetch detailed college info from MongoDB
    try:
        college = college_details_col.find_one({"college": {"$regex": college_name, "$options": "i"}})
        
        if college:
            return render_template("college_details.html", college=college)
    except:
        pass
    
    # Fallback if not found in detailed collection
    college_basic = intents_col.find_one({"college": college_name})
    if college_basic:
        return render_template("college_details.html", college=college_basic)
    
    # Final fallback - dummy data
    college = {
        "college": college_name,
        "fees_per_year": "₹1,20,000 / year",
        "avg_package": "8 LPA",
        "placement_rate": "85%",
        "hostel_available": True,
        "hostel_fee": "₹50,000",
        "city": "Maharashtra"
    }
    return render_template("college_details.html", college=college)


@app.route("/college-enquiry", methods=["POST"])
def college_enquiry():
    """Handle college-specific questions using intelligent chatbot"""
    try:
        data = request.get_json()
        college_name = data.get("college", "")
        branch = data.get("branch", "")
        category = data.get("category", "OPEN")
        question = data.get("question", "")
        
        if not college_name or not question:
            return jsonify({
                "success": False,
                "message": "College name and question are required"
            }), 400

        log_user_search("college_enquiry", question, college=college_name, branch=branch, category=category)
        
        # Get intelligent response from college chatbot
        response = answer_college_query(question, college_name, branch, category)
        
        return jsonify({
            "success": True,
            "college": college_name,
            "question": question,
            "answer": response
        })
        
    except Exception as e:
        print(f"Error in college enquiry: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@app.route("/advanced-chatbot")
def advanced_chatbot():
    """Advanced interactive chatbot with real-time verification"""
    return render_template("advanced_chatbot.html")


@app.route("/advanced-college-enquiry", methods=["POST"])
def advanced_college_enquiry():
    """Handle college queries with real-time web verification"""
    try:
        data = request.get_json()
        college_name = data.get("college", "")
        question = data.get("question", "")
        
        if not college_name or not question:
            return jsonify({
                "success": False,
                "message": "College name and question are required"
            }), 400

        log_user_search("advanced_college_enquiry", question, college=college_name)
        
        # Use advanced chatbot with real-time verification
        chatbot = AdvancedCollegeChatbot()
        response_data = chatbot.answer_with_verification(question, college_name)
        
        return jsonify({
            "success": True,
            "college": response_data['college'],
            "question": question,
            "answer": response_data['answer'],
            "verified": response_data['verified'],
            "sources": response_data['sources'],
            "sources_count": len(response_data['sources']),
            "followup": response_data['followup'],
            "type": response_data['type']
        })
        
    except Exception as e:
        print(f"Error in advanced college enquiry: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        # Get data from form
        name = request.form["name"]
        email = request.form["email"]
        percentile = float(request.form["percentile"])
        category = request.form["category"]
        branch = request.form["branch"]
        city = request.form.get("city", "")
        exam_type = request.form.get("exam_type", "MHT-CET")

        # Save student data in MongoDB
        student_doc = {
            "name": name,
            "email": email,
            "percentile": percentile,
            "exam_type": exam_type,
            "category": category,
            "branch": branch,
            "city": city,
            "timestamp": datetime.now()
        }

        student_result = students_col.insert_one(student_doc)
        student_id = student_result.inserted_id

        # Get recommended colleges (from MongoDB)
        colleges = recommend_colleges(percentile, category, branch, city, exam_type)

        # Store the student data and colleges for report generation
        session['student_id'] = str(student_id)
        session['student_data'] = {
            'name': name,
            'email': email,
            'percentile': percentile,
            'exam_type': exam_type,
            'category': category,
            'branch': branch,
            'city': city
        }
        session['colleges'] = colleges

        # Save search history for logged-in users
        if current_user.is_authenticated:
            from mongo_db import users_col
            search_entry = {
                "timestamp": datetime.now(),
                "percentile": percentile,
                "exam_type": exam_type,
                "category": category,
                "branch": branch,
                "city": city,
                "colleges_found": len(colleges)
            }
            users_col.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$push": {"search_history": search_entry}}
            )

        return render_template("colleges.html", colleges=colleges, student_name=name, city=city)

    except Exception as e:
        print(f"Error in recommend route: {str(e)}")
        return render_template("error.html", error=str(e)), 500


def log_user_search(source, query, college=None, branch=None, category=None):
    try:
        if not query or not query.strip():
            return

        search_logs_col.insert_one({
            "source": source,
            "query": query.strip(),
            "college": college,
            "branch": branch,
            "category": category,
            "timestamp": datetime.now()
        })
    except Exception as e:
        print(f"⚠️  Search log error: {e}")


@app.route("/generate-report", methods=["POST"])
def generate_report():
    """Generate PDF report and send via email"""
    try:
        # Get student data from session
        if 'student_data' not in session or 'colleges' not in session:
            return jsonify({"success": False, "message": "Session expired. Please submit the form again."}), 400

        student_data = session['student_data']
        colleges = session['colleges']

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{student_data['name'].replace(' ', '_')}_{timestamp}.pdf"
        report_path = os.path.join(REPORTS_DIR, report_filename)

        print(f"\n{'='*60}")
        print(f"📄 GENERATING REPORT FOR {student_data['name']}")
        print(f"{'='*60}")

        # Generate PDF report
        try:
            print(f"🔨 Creating PDF at: {report_path}")
            generate_report_with_details(student_data, colleges, report_path)
            print(f"✅ PDF created successfully")
        except Exception as pdf_error:
            error_msg = f"PDF generation failed: {str(pdf_error)}"
            print(f"❌ {error_msg}")
            return jsonify({
                "success": False,
                "message": error_msg
            }), 500

        # Send email with report
        print(f"\n{'='*60}")
        print(f"📧 SENDING EMAIL")
        print(f"{'='*60}")
        
        email_success = False
        email_error_msg = None
        
        try:
            email_success = send_report_email(
                student_email=student_data['email'],
                student_name=student_data['name'],
                report_path=report_path,
                colleges_list=colleges
            )
        except Exception as email_error:
            email_error_msg = str(email_error)
            print(f"\n⚠️  Email Error: {email_error_msg}")
        
        # Update student record with report status
        try:
            students_col.update_one(
                {"_id": ObjectId(session.get('student_id'))},
                {"$set": {
                    "report_generated": True,
                    "report_path": report_path,
                    "email_status": "sent" if email_success else "failed",
                    "report_generated_at": datetime.now()
                }}
            )
        except Exception as db_error:
            print(f"⚠️  Database update error: {str(db_error)}")
        
        print(f"\n{'='*60}")
        
        # Return success regardless of email status since PDF was generated
        if email_success:
            print(f"✅ SUCCESS! Report sent to {student_data['email']}")
            return jsonify({
                "success": True,
                "message": f"✅ Report successfully sent to {student_data['email']}!",
                "report_file": report_filename,
                "email_status": "sent"
            })
        else:
            # PDF generated but email failed - still a partial success
            print(f"⚠️  Report created but email delivery failed")
            return jsonify({
                "success": True,
                "message": f"✅ Report generated successfully! (Saved locally)\n⚠️  Email delivery failed. Your PDF is saved at:\n{report_path}",
                "report_file": report_filename,
                "email_status": "failed",
                "local_path": report_path
            })

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"\n🚨 {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": error_msg}), 500


@app.route("/chatbot/<college>", methods=["GET", "POST"])
def chatbot(college):
    reply = ""

    if request.method == "POST":
        user_msg = request.form["message"]

        log_user_search("college_chat", user_msg, college=college)

        # Fetch intents from MongoDB
        intents = list(
            intents_col.find(
                {"college": college},
                {"_id": 0, "pattern": 1, "response": 1}
            )
        )

        reply = get_response(user_msg, intents)

    return render_template("chatbot.html", college=college, reply=reply)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        from mongo_db import users_col

        # Check if username or email already exists
        existing_user = users_col.find_one({
            "$or": [
                {"username": form.username.data},
                {"email": form.email.data}
            ]
        })

        if existing_user:
            flash('Username or email already exists. Please choose different ones.', 'error')
            return redirect(url_for('register'))

        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        user_doc = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "name": form.name.data,
            "created_at": datetime.now(),
            "favorites": [],  # For wishlist feature
            "search_history": []
        }

        result = users_col.insert_one(user_doc)
        user_data = users_col.find_one({"_id": result.inserted_id})

        user = User(user_data)
        login_user(user)

        flash('Registration successful! Welcome to College Recommendation System.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        from mongo_db import users_col

        user_data = users_col.find_one({"username": form.username.data})

        if user_data and check_password_hash(user_data['password'], form.password.data):
            user = User(user_data)
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's recent searches and favorites
    from mongo_db import users_col

    user_data = users_col.find_one({"_id": ObjectId(current_user.id)})
    recent_searches = user_data.get('search_history', [])[-5:]  # Last 5 searches
    favorites = user_data.get('favorites', [])

    # Get favorite colleges details
    favorite_colleges = []
    if favorites:
        for college_name in favorites:
            college = college_details_col.find_one({"college": {"$regex": college_name, "$options": "i"}})
            if college:
                favorite_colleges.append(college)

    return render_template('dashboard.html',
                         user=current_user,
                         recent_searches=recent_searches,
                         favorite_colleges=favorite_colleges)


@app.route('/add_favorite/<college_name>')
@login_required
def add_favorite(college_name):
    from mongo_db import users_col

    users_col.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$addToSet": {"favorites": college_name}}
    )

    flash(f'{college_name} added to favorites!', 'success')
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/remove_favorite/<college_name>')
@login_required
def remove_favorite(college_name):
    from mongo_db import users_col

    users_col.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$pull": {"favorites": college_name}}
    )

    flash(f'{college_name} removed from favorites.', 'info')
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/compare')
@login_required
def compare():
    # Get colleges to compare from session or query params
    college1 = request.args.get('college1', '')
    college2 = request.args.get('college2', '')

    colleges_data = []
    if college1:
        col1 = college_details_col.find_one({"college": {"$regex": college1, "$options": "i"}})
        if col1:
            colleges_data.append(col1)

    if college2:
        col2 = college_details_col.find_one({"college": {"$regex": college2, "$options": "i"}})
        if col2:
            colleges_data.append(col2)

    return render_template('compare.html', colleges=colleges_data)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        college = request.form["college"]
        pattern = request.form["pattern"]
        response = request.form["response"]

        intents_col.insert_one({
            "college": college,
            "pattern": pattern,
            "response": response,
            "created_at": datetime.now()
        })

    data = list(intents_col.find({}, {"_id": 0}))
    recent_searches = []
    emails_sent = 0

    try:
        for log in search_logs_col.find({}, {"_id": 0}).sort("timestamp", -1).limit(10):
            log["timestamp"] = log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            recent_searches.append(log)
    except Exception as e:
        print(f"⚠️  Could not fetch search logs: {e}")

    try:
        emails_sent = students_col.count_documents({"email_status": "sent"})
    except Exception as e:
        print(f"⚠️  Could not count sent emails: {e}")

    return render_template("admin_panel.html", data=data, recent_searches=recent_searches, emails_sent=emails_sent)


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error="Page not found"), 404


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 Server errors"""
    import logging
    logging.error(f"Server error: {str(error)}")
    return render_template("500.html"), 500


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    return render_template("error.html", error="Access Forbidden"), 403


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return render_template("error.html", error="Bad Request"), 400


@app.context_processor
def inject_user():
    """Make current_user available in templates"""
    return dict(current_user=current_user)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, use_reloader=False, port=5000)
