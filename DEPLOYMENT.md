# Deployment Guide

## Production Deployment

### 1. Local Setup for Production

```bash
# Activate virtual environment
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Mac/Linux

# Install production dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 2. Environment variables for Production

Create `.env` file with production values:
```env
FLASK_ENV=production
SECRET_KEY=<generate_secure_random_key>
MONGODB_URI=<production_mongodb_uri>
GEMINI_API_KEY=<your_api_key>

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Security
DEBUG=False
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

### 3. Deploy to Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Add MongoDB addon
heroku addons:create mongolab:sandbox

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### 4. Deploy with Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t college-recommendation .
docker run -p 5000:5000 -e MONGODB_URI="..." college-recommendation
```

### 5. Deploy to AWS EC2

```bash
# SSH into instance
ssh -i key.pem ec2-user@your-instance-ip

# Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip -y

# Clone repository
git clone https://github.com/your-repo.git
cd college-recommendation-system

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

### 6. Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /path/to/app/static/;
    }
}
```

### 7. SSL/HTTPS Setup with Let's Encrypt

```bash
sudo yum install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d your-domain.com
```

### 8. Monitoring & Performance

**Install monitoring tools:**
```bash
pip install sentry-sdk flask-monitoring-dashboard
```

**Configure Sentry:**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()]
)
```

### 9. Database Backups

**MongoDB Backup:**
```bash
mongodump --uri="mongodb://..." --out=./backup

# Schedule daily backups with cron
0 2 * * * /path/to/backup-script.sh
```

### 10. Performance Optimization

- Enable gzip compression
- Use CDN for static files
- Implement caching headers
- Database query optimization
- Use Redis for session storage

### 11. Health Checks

```bash
# Monitor endpoint
curl https://your-app.com/api/health

# Set up pingdom or similar for uptime monitoring
```

### 12. Scaling

**Horizontal Scaling:**
- Load balance multiple instances with Nginx/HAProxy
- Use Docker swarm or Kubernetes

**Vertical Scaling:**
- Upgrade server resources
- Optimize database queries

---

## Troubleshooting

### Common Deployment Issues

**Port Already in Use:**
```bash
lsof -i :5000
kill -9 <PID>
```

**Import Errors:**
```bash
pip install -r requirements.txt --force-reinstall
```

**Database Connection:**
```bash
# Test connection
python -c "from mongo_db import db; print(db.collection_names())"
```

**Logs:**
```bash
tail -f /var/log/app.log
journalctl -u app -n 100
```

---

## Maintenance

### Regular Tasks

- **Weekly**: Monitor error logs, check performance metrics
- **Monthly**: Update dependencies, review security patches
- **Quarterly**: Database optimization, backup verification

### Update Procedure

```bash
git pull origin main
pip install -r requirements.txt --upgrade
pytest tests/
# Restart application
```

---

For more details, see individual platform documentation.
