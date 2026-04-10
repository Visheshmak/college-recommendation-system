# Database Schema & Collections

## Overview

This document describes the MongoDB collections and their schema for the College Recommendation System.

---

## Collections

### 1. **students** Collection

Stores student profile information and exam details.

```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  name: String,
  password_hash: String,
  percentile: Number,
  exam_type: String,  // "MHT-CET", "JEE Main", "JEE Advanced"
  category: String,   // "General", "OBC", "SC", "ST", "PWD"
  preferred_branch: String,  // "CSE", "ECE", "ME", etc.
  preferred_city: String,
  created_at: Date,
  updated_at: Date,
  is_active: Boolean
}
```

**Indexes:**
```javascript
db.students.createIndex({ email: 1 }, { unique: true })
db.students.createIndex({ username: 1 }, { unique: true })
db.students.createIndex({ created_at: -1 })
```

---

### 2. **colleges** Collection

Main collection for college information and cutoff data.

```javascript
{
  _id: ObjectId,
  name: String,
  code: String,              // College code
  city: String,
  district: String,
  state: String,
  established_year: Number,
  college_type: String,      // "Govt", "Private", "Grant-in-aid"
  
  // Academic Details
  branches: [String],        // ["CSE", "ECE", "ME"]
  seats: {
    cse: Number,
    ece: Number,
    me: Number,
    // ... other branches
  },
  
  // Cutoff Data
  cutoffs: {
    general: {
      branch: Number,        // Cut-off percentile
      open: Number,
      management: Number
    },
    obc: { ... },
    sc: { ... },
    st: { ... }
  },
  
  // Placement Info
  avg_package: Number,       // In LPA
  highest_package: Number,
  placement_rate: Number,    // Percentage
  recruiting_companies: [String],
  
  // Infrastructure
  hostel_available: Boolean,
  hostel_capacity: Number,
  hostel_fees: Number,
  
  // Fees
  fees_per_year: Number,
  total_fees: Number,
  
  // Contact
  website: String,
  email: String,
  phone: String,
  principal_name: String,
  
  // Ratings and Reviews
  rating: Number,            // 0-5
  reviews_count: Number,
  
  created_at: Date,
  updated_at: Date
}
```

**Indexes:**
```javascript
db.colleges.createIndex({ name: 1 })
db.colleges.createIndex({ city: 1 })
db.colleges.createIndex({ branches: 1 })
db.colleges.createIndex({ rating: -1 })
db.colleges.createIndex({ "cutoffs.general.open": 1 })
```

---

### 3. **college_details** Collection

Detailed information about each college (academic programs, facilities, etc.).

```javascript
{
  _id: ObjectId,
  college: String,          // Reference to college name
  college_id: ObjectId,     // Reference to colleges._id
  
  // Academic Programs
  programs: [
    {
      name: String,         // "B.Tech in CSE"
      duration: Number,     // 4 years
      specializations: [String],
      eligibility: String,
      syllabus_url: String
    }
  ],
  
  // Facilities
  facilities: [String],     // ["Library", "Lab", "Sports Ground"]
  library: {
    books: Number,
    digital_resources: Boolean,
    online_databases: [String]
  },
  
  // Placements Details
  placement_info: {
    companies_visited: [String],
    avg_ctc: Number,
    highest_ctc: Number,
    median_ctc: Number,
    placement_percentage: Number,
    internship_rate: Number
  },
  
  // Faculty
  faculty_count: Number,
  phd_faculty: Number,
  student_teacher_ratio: Number,
  
  // Admissions Info
  admission_process: String,  // Description
  documents_required: [String],
  important_dates: [
    {
      event: String,
      date: Date
    }
  ],
  
  // Reviews Summary
  reviews_summary: {
    academic_quality: Number,
    campus_life: Number,
    infrastructure: Number,
    placement_support: Number
  },
  
  updated_at: Date
}
```

---

### 4. **users** Collection

User account management (extends students with authentication).

```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  name: String,
  password_hash: String,
  avatar_url: String,
  
  // Profile
  phone: String,
  address: String,
  city: String,
  
  // Preferences
  preferences: {
    email_notifications: Boolean,
    dark_mode: Boolean,
    language: String
  },
  
  // Account Status
  is_verified: Boolean,
  is_active: Boolean,
  role: String,              // "student", "admin"
  
  // Timestamps
  created_at: Date,
  updated_at: Date,
  last_login: Date,
  
  // Security
  two_factor_enabled: Boolean,
  password_reset_token: String,
  password_reset_expires: Date
}
```

**Indexes:**
```javascript
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ username: 1 }, { unique: true })
```

---

### 5. **saved_colleges** Collection

Bookmarked/saved colleges for users.

```javascript
{
  _id: ObjectId,
  user_id: String,           // Reference to users._id
  college_id: ObjectId,      // Reference to colleges._id
  college_name: String,
  notes: String,            // User's personal notes
  tags: [String],           // Custom tags
  saved_at: Date,
  rating_preference: Number  // 0-5
}
```

**Indexes:**
```javascript
db.saved_colleges.createIndex({ user_id: 1, college_id: 1 }, { unique: true })
db.saved_colleges.createIndex({ user_id: 1 })
db.saved_colleges.createIndex({ saved_at: -1 })
```

---

### 6. **reviews** Collection

College reviews and ratings from users.

```javascript
{
  _id: ObjectId,
  college_id: ObjectId,     // Reference to colleges._id
  college_name: String,
  user_id: String,          // Reference to users._id
  username: String,
  
  // Review Content
  title: String,
  description: String,
  rating: Number,           // 0-5
  
  // Category Ratings
  academic_quality: Number,
  campus_life: Number,
  infrastructure: Number,
  placement_support: Number,
  
  // Metadata
  verified_after_admission: Boolean,
  batch_year: Number,       // e.g., 2020
  branch: String,
  placement_status: String, // "Placed", "Self-Employed", "Not Placed"
  ctc: Number,
  
  // Review Management
  helpful_count: Number,
  unhelpful_count: Number,
  is_approved: Boolean,
  is_flagged: Boolean,
  
  created_at: Date,
  updated_at: Date
}
```

**Indexes:**
```javascript
db.reviews.createIndex({ college_id: 1 })
db.reviews.createIndex({ user_id: 1 })
db.reviews.createIndex({ rating: -1 })
db.reviews.createIndex({ created_at: -1 })
```

---

### 7. **search_logs** Collection

Logs search queries for analytics.

```javascript
{
  _id: ObjectId,
  user_id: String,          // Optional, null for anonymous
  query: String,
  filters: Object,          // Applied filters
  results_count: Number,
  clicked_result_index: Number,  // Which result user clicked
  session_id: String,
  ip_address: String,
  user_agent: String,
  created_at: Date
}
```

**Indexes:**
```javascript
db.search_logs.createIndex({ created_at: -1 })
db.search_logs.createIndex({ user_id: 1 })
db.search_logs.createIndex({ query: 1 })
```

---

### 8. **intents** Collection

Trained intents for chatbot.

```javascript
{
  _id: ObjectId,
  type: String,             // "college_qa", "general", "placement"
  pattern: String,          // Search/match pattern
  response: String,         // Chatbot response
  category: String,         // e.g., "fees", "admission", "placements"
  parent_college: String,   // Optional: for college-specific intents
  created_at: Date,
  updated_by: String,
  confidence_score: Number
}
```

---

### 9. **recommendations** Collection

Stores generated recommendations for analytics.

```javascript
{
  _id: ObjectId,
  user_id: String,
  percentile: Number,
  category: String,
  branch: String,
  city: String,
  
  recommendations: [
    {
      college_name: String,
      probability: String,  // "High", "Medium", "Low"
      cutoff_required: Number,
      rank: Number
    }
  ],
  
  generated_at: Date,
  clicked_colleges: [String]  // For tracking engagement
}
```

---

## Data Types Reference

| Type | MongoDB | Python |
|------|---------|--------|
| Unique Identifier | ObjectId | ObjectId |
| Text | String | str |
| Number | Number | int, float |
| Boolean | Boolean | bool |
| Date | Date | datetime |
| Array | Array | list |
| Object | Object | dict |
| Null | Null | None |

---

## Relationships

```
users (1) ------ (many) saved_colleges
           ------ (many) reviews
           ------ (many) search_logs
           ------ (many) recommendations

colleges (1) ------ (many) college_details
          ------ (many) reviews
          ------ (many) saved_colleges
```

---

## Backup & Recovery

### Backup MongoDB Atlas

```bash
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/dbname" \
          --out=./backup_$(date +%Y%m%d)
```

### Restore

```bash
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/dbname" \
             ./backup_20260410
```

---

## Performance Optimization

### Query Optimization

```javascript
// Good: Uses index
db.colleges.find({ city: "Mumbai", rating: { $gte: 4.0 } })

// Bad: Inefficient
db.colleges.find({ $where: "this.city == 'Mumbai'" })
```

### Aggregation Pipeline

```javascript
db.colleges.aggregate([
  { $match: { city: "Mumbai" } },
  { $group: { _id: "$city", avg_rating: { $avg: "$rating" } } },
  { $sort: { avg_rating: -1 } }
])
```

---

## Maintenance

### Drop Collection
```javascript
db.search_logs.drop()  // Remove all search logs
```

### Rebuild Indexes
```javascript
db.colleges.reIndex()
```

### Monitor Collection Size
```javascript
db.colleges.stats()
```

---

For more MongoDB documentation, visit: https://docs.mongodb.com/
