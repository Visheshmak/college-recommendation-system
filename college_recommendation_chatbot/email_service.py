import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from mongo_db import MAIL_CONFIG
import sys
import socket
import os


def check_internet_connection():
    """Check if internet connection is available"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def check_smtp_server(server_name, port):
    """Check if SMTP server is reachable"""
    try:
        socket.create_connection((server_name, port), timeout=5)
        return True
    except OSError as e:
        print(f"   ⚠️  Cannot reach {server_name}:{port}")
        print(f"   Error: {e}")
        return False


def get_sender_email():
    sender = MAIL_CONFIG.get('MAIL_DEFAULT_SENDER') or MAIL_CONFIG.get('MAIL_USERNAME')
    if sender and '@' in sender:
        return sender
    return MAIL_CONFIG.get('MAIL_USERNAME', '')


def build_recommendation_summary(colleges_list):
    lines = []
    for college in colleges_list[:5]:
        college_name = college.get('college', college.get('name', 'College'))
        branch = college.get('branch', 'Branch')
        category = college.get('category', 'OPEN')
        cutoff = college.get('cutoff', college.get('cutoff_percentile', 'N/A'))
        chance = college.get('chance', college.get('admission_chance', 'N/A'))
        lines.append(f"• {college_name} | {branch} | {category} | Cutoff: {cutoff} | Chance: {chance}")
    return "\n".join(lines)


def send_report_email(student_email, student_name, report_path, colleges_list):
    """Send the recommendation report to the student's email."""
    sender_email = get_sender_email()
    recipient_email = student_email.strip()

    if not recipient_email or '@' not in recipient_email:
        raise ValueError('Invalid recipient email address')

    print(f"\n📧 Sending email to {recipient_email}...")
    print(f"   From: {sender_email}")
    print(f"   Server: {MAIL_CONFIG['MAIL_SERVER']}:{MAIL_CONFIG['MAIL_PORT']}")

    if not check_internet_connection():
        print("   ⚠️ No internet connection detected.")
        return False

    if not check_smtp_server(MAIL_CONFIG['MAIL_SERVER'], MAIL_CONFIG['MAIL_PORT']):
        print(f"   ⚠️ Cannot reach SMTP server {MAIL_CONFIG['MAIL_SERVER']}:{MAIL_CONFIG['MAIL_PORT']}")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"College Recommendation Report for {student_name}"
    msg['Reply-To'] = sender_email

    summary = build_recommendation_summary(colleges_list)
    body = (
        f"Hello {student_name},\n\n"
        f"Your personalized college recommendation report is ready.\n"
        f"Please see the attached PDF for full details.\n\n"
        f"Top recommendations:\n{summary}\n\n"
        f"Regards,\n"
        f"College Recommendation System"
    )

    msg.attach(MIMEText(body, 'plain'))

    if os.path.isfile(report_path):
        try:
            with open(report_path, 'rb') as attachment_file:
                attachment = MIMEBase('application', 'pdf')
                attachment.set_payload(attachment_file.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(report_path)}"'
            )
            msg.attach(attachment)
            print(f"   📎 Attached report: {os.path.basename(report_path)}")
        except Exception as e:
            print(f"   ⚠️ Could not attach report: {e}")
    else:
        print(f"   ⚠️ Report file does not exist: {report_path}")

    try:
        with smtplib.SMTP(MAIL_CONFIG['MAIL_SERVER'], MAIL_CONFIG['MAIL_PORT'], timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(MAIL_CONFIG['MAIL_USERNAME'], MAIL_CONFIG['MAIL_PASSWORD'])
            server.sendmail(sender_email, recipient_email, msg.as_string())

        print(f"   ✅ Email sent successfully to {recipient_email}\n")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: Invalid email credentials")
        print(f"   Details: {e}")
        print(f"   Solution: Regenerate Gmail App Password from https://myaccount.google.com/apppasswords")
        return False
    except smtplib.SMTPException as e:
        print(f"   ❌ SMTP error: {e}")
        print(f"   Solution: Check firewall settings or try a different port (465 instead of 587)")
        return False
    except socket.timeout:
        print(f"   ❌ Connection timeout: SMTP server took too long to respond")
        print(f"   Solution: Check internet connection and firewall settings")
        return False
    except Exception as e:
        print(f"   ❌ Error sending email: {str(e)[:100]}")
        print(f"   Tip: Reports are still saved locally in the reports folder")
        return False


def send_welcome_email(student_email, student_name):
    """Send a short welcome email when a student registers."""
    sender_email = get_sender_email()
    recipient_email = student_email.strip()

    if not recipient_email or '@' not in recipient_email:
        print('Invalid welcome email address.')
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Welcome to College Recommendation System, {student_name}!"
    msg['Reply-To'] = sender_email

    body = (
        f"Hello {student_name},\n\n"
        f"Welcome! Your profile is ready, and you can request a personalized college recommendation report.\n\n"
        f"Best regards,\n"
        f"College Recommendation System"
    )

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(MAIL_CONFIG['MAIL_SERVER'], MAIL_CONFIG['MAIL_PORT'], timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(MAIL_CONFIG['MAIL_USERNAME'], MAIL_CONFIG['MAIL_PASSWORD'])
            server.sendmail(sender_email, recipient_email, msg.as_string())

        return True

    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
