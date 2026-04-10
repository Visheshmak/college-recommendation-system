# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Some endpoints require authentication. Include your session cookie or JWT token in request headers.

---

## Endpoints

### 1. Get Colleges

**Endpoint:** `GET /colleges`

**Description:** Retrieve a list of colleges with optional filters

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| city | string | No | Filter by city name |
| branch | string | No | Filter by engineering branch |
| min_rating | float | No | Minimum rating (0-5) |
| limit | integer | No | Number of results (default: 20, max: 100) |
| offset | integer | No | Pagination offset (default: 0) |

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/colleges?city=Mumbai&branch=CSE&limit=10"
```

**Example Response:**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "colleges": [
      {
        "_id": "507f1f77bcf86cd799439011",
        "name": "COEP",
        "city": "Mumbai",
        "branch": "CSE",
        "fees": 1500000,
        "placements": "95%",
        "rating": 4.8
      }
    ],
    "total": 25,
    "limit": 10,
    "offset": 0
  },
  "timestamp": "2026-04-10T10:30:00"
}
```

**Status Codes:**
- 200: Success
- 400: Bad request
- 500: Server error

---

### 2. Get College Details

**Endpoint:** `GET /college/<college_name>`

**Description:** Get detailed information about a specific college

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| college_name | string | Yes | Name of the college |

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/college/COEP"
```

**Example Response:**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "college": "COEP",
    "city": "Mumbai",
    "branches": ["CSE", "ECE", "ME"],
    "fees_per_year": 150000,
    "avg_package": "12 LPA",
    "placement_rate": "95%",
    "hostel_available": true,
    "hostel_fees": 60000,
    "cutoff": 98.5,
    "contact": "contact@coep.ac.in"
  },
  "timestamp": "2026-04-10T10:30:00"
}
```

**Status Codes:**
- 200: Success
- 404: College not found
- 500: Server error

---

### 3. Search Colleges (Advanced)

**Endpoint:** `POST /search`

**Description:** Advanced search with multiple filters

**Request Body:**
```json
{
  "query": "search term",
  "filters": {
    "city": "Mumbai",
    "branch": "CSE",
    "fees_min": 1000000,
    "fees_max": 2000000,
    "rating_min": 4.0,
    "category": "General"
  },
  "limit": 20,
  "offset": 0
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "engineering",
    "filters": {
      "city": "Mumbai",
      "branch": "CSE"
    },
    "limit": 10
  }'
```

**Example Response:**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "results": [...],
    "total": 5,
    "limit": 10,
    "offset": 0,
    "query": "engineering"
  },
  "timestamp": "2026-04-10T10:30:00"
}
```

**Status Codes:**
- 200: Success
- 400: Validation error
- 500: Server error

---

### 4. Get Recommendations

**Endpoint:** `POST /recommend`

**Description:** Get college recommendations based on student criteria

**Request Body:**
```json
{
  "percentile": 95.5,
  "category": "General",
  "branch": "CSE",
  "city": "Mumbai"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| percentile | number | Yes | Exam percentile (0-100) |
| category | string | Yes | Student category (General, OBC, SC, ST) |
| branch | string | Yes | Preferred branch |
| city | string | No | Preferred city |

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "percentile": 95.5,
    "category": "General",
    "branch": "CSE",
    "city": "Mumbai"
  }'
```

**Example Response:**
```json
{
  "success": true,
  "message": "Recommendations generated successfully",
  "data": {
    "recommendations": [
      {
        "name": "COEP",
        "probability": "High",
        "cutoff": 98.5
      },
      {
        "name": "VJTI",
        "probability": "Medium",
        "cutoff": 96.2
      }
    ],
    "count": 2
  },
  "timestamp": "2026-04-10T10:30:00"
}
```

**Status Codes:**
- 200: Success
- 400: Validation error
- 500: Server error

---

### 5. Saved Colleges

**Endpoint:** `GET /saved-colleges` or `POST /saved-colleges`

**Description:** Get or add saved colleges for authenticated user

**Authentication:** Required

**GET Request:**
```bash
curl -X GET "http://localhost:5000/api/saved-colleges" \
  -H "Cookie: session=your_session_cookie"
```

**GET Response:**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "saved_colleges": [
      {
        "_id": "507f1f77bcf86cd799439011",
        "college_id": "507f1f77bcf86cd799439012",
        "saved_at": "2026-04-10T10:30:00"
      }
    ]
  },
  "timestamp": "2026-04-10T10:30:00"
}
```

**POST Request:**
```bash
curl -X POST "http://localhost:5000/api/saved-colleges" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_cookie" \
  -d '{
    "college_id": "507f1f77bcf86cd799439012"
  }'
```

**Status Codes:**
- 200: Success (GET)
- 201: Created (POST)
- 401: Unauthorized
- 409: College already saved
- 500: Server error

---

### 6. Health Check

**Endpoint:** `GET /health`

**Description:** Check API health status

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/health"
```

**Example Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-04-10T10:30:00"
}
```

**Status Codes:**
- 200: API is healthy

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-04-10T10:30:00"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| VALIDATION_ERROR | 400 | Input validation failed |
| AUTH_REQUIRED | 401 | Authentication required |
| FORBIDDEN | 403 | Access forbidden |
| NOT_FOUND | 404 | Resource not found |
| ALREADY_SAVED | 409 | College already saved |
| DB_ERROR | 500 | Database error |
| SERVER_ERROR | 500 | Internal server error |

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Standard endpoints: 100 requests per hour per IP
- Search/Recommend: 50 requests per hour per IP
- Saved colleges: Default rate limit

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1680000000
```

When rate limit is exceeded:
```json
{
  "success": false,
  "error": "Rate limit exceeded. Try again later.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```
Status Code: 429

---

## Authentication

### Session-based Authentication
The API supports Flask-Login session-based authentication. Login first, then include your session cookie in requests.

### Example Authentication Flow:
```bash
# 1. Login
curl -X POST "http://localhost:5000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=youruser&password=yourpass" \
  -c cookies.txt

# 2. Use saved cookies in subsequent requests
curl -X GET "http://localhost:5000/api/saved-colleges" \
  -b cookies.txt
```

---

## Pagination

For endpoints that return lists, use `limit` and `offset`:

```bash
# Get first 20 results
/colleges?limit=20&offset=0

# Get next 20 results
/colleges?limit=20&offset=20
```

---

## Filtering

### Supported Filters

**City Filter:**
```
city=Mumbai  # Case-insensitive partial match
```

**Branch Filter:**
```
branch=CSE  # Exact match, case-insensitive
```

**Rating Filter:**
```
min_rating=4.0  # Returns colleges with rating >= 4.0
```

**Fees Range:**
```
# In POST search endpoint
"filters": {
  "fees_min": 1000000,
  "fees_max": 2000000
}
```

---

## Testing the API

### Using cURL
```bash
# Get colleges
curl "http://localhost:5000/api/colleges?limit=5"

# Search colleges
curl -X POST "http://localhost:5000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query":"Mumbai","limit":10}'

# Get recommendations
curl -X POST "http://localhost:5000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{"percentile":95,"category":"General","branch":"CSE"}'
```

### Using Python Requests
```python
import requests

# Get colleges
response = requests.get('http://localhost:5000/api/colleges', 
  params={'city': 'Mumbai', 'limit': 10})
print(response.json())

# Search
payload = {
  'query': 'engineering',
  'filters': {'branch': 'CSE'},
  'limit': 10
}
response = requests.post('http://localhost:5000/api/search', json=payload)
print(response.json())
```

---

## API Versioning

- Current Version: 1.0.0
- Base URL includes version in future releases: `/api/v1/...`

---

## Support

For API issues or questions:
- Create an issue on GitHub
- Check existing documentation
- Review code examples

---

Last Updated: 2026-04-10
