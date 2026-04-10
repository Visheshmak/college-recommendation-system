from mongo_db import colleges_col

# Branch name mapping for fuzzy matching
BRANCH_MAPPING = {
    "computer engineering": "computer engineering",
    "information technology": "information technology",
    "it": "information technology",
    "computer science": "computer science",
    "cs": "computer science",
    "ai & ds": "computer science",
    "ai and ds": "computer science",
    "artificial intelligence": "computer science",
    "electronics": "electronics engineering",
    "electronics engineering": "electronics engineering",
    "mechanical": "mechanical engineering",
    "mechanical engineering": "mechanical engineering",
    "instrumentation": "instrumentation engineering",
    "instrumentation engineering": "instrumentation engineering",
    "textile": "textile technology",
    "textile technology": "textile technology",
    "metallurgical": "metallurgical engineering",
    "metallurgical engineering": "metallurgical engineering",
}

def normalize_branch(branch):
    branch_lower = branch.lower().strip()
    return BRANCH_MAPPING.get(branch_lower, branch_lower)

def calculate_chance(student_percentile, cutoff, exam_type="MHT-CET"):
    exam_type = exam_type.upper().strip() if exam_type else "MHT-CET"
    if exam_type == "JEE ADVANCED":
        diff = cutoff - student_percentile
        if diff >= 0:
            return "Very High"
        elif diff >= -100:
            return "High"
        elif diff >= -300:
            return "Medium"
        elif diff >= -700:
            return "Low"
        else:
            return "Very Low"
    else:
        diff = student_percentile - cutoff
        if diff >= 0:
            return "Very High"
        elif diff >= 5:
            return "High"
        elif diff >= 10:
            return "Medium"
        elif diff >= 15:
            return "Low"
        else:
            return "Very Low"
    

def calculate_match_score(student_percentile, student_category, normalized_branch, 
                         student_city, college_data, college_percentile, 
                         college_category, college_branch, college_city, exam_type="MHT-CET"):
    """
    Calculate a composite match score for a college (0-100)
    Higher score = better match
    """
    score = 0
    exam_type = exam_type.upper().strip() if exam_type else "MHT-CET"

    # 1. PERCENTILE / RANK MATCH (0-40 points)
    if exam_type == "JEE ADVANCED":
        rank_diff = college_percentile - student_percentile
        if rank_diff >= 0:
            score += 40
        elif rank_diff >= -100:
            score += 30
        elif rank_diff >= -300:
            score += 20
        elif rank_diff >= -700:
            score += 10
    else:
        percentile_diff = student_percentile - college_percentile
        if percentile_diff >= 0:
            score += 40  # Student meets/exceeds cutoff
        elif percentile_diff >= -2:
            score += 30  # Within 2% below cutoff
        elif percentile_diff >= -5:
            score += 20  # Within 5% below cutoff
        elif percentile_diff >= -10:
            score += 10  # Within 10% below cutoff

    # 2. CATEGORY MATCH (0-25 points)
    if student_category == college_category:
        score += 25  # Exact category match
    else:
        score += 5   # Different category but acceptable

    # 3. BRANCH MATCH (0-20 points)
    college_branch_lower = college_branch.lower()
    if normalized_branch in college_branch_lower or college_branch_lower in normalized_branch or \
       normalized_branch == college_branch_lower:
        score += 20  # Exact branch match
    else:
        score += 0   # Branch doesn't match

    # 4. CITY PREFERENCE (0-15 points)
    if student_city:  # Only score if user selected a city
        if student_city == college_city.lower():
            score += 15  # City match
        else:
            score += 0   # City doesn't match
    else:
        score += 15  # No city preference = no penalty

    return score
    """
    Calculate a composite match score for a college (0-100)
    Higher score = better match
    """
    score = 0
    
    # 1. PERCENTILE MATCH (0-40 points)
    # Exact match at or above cutoff is best
    percentile_diff = student_percentile - college_percentile
    if percentile_diff >= 0:
        score += 40  # Student meets/exceeds cutoff
    elif percentile_diff >= -2:
        score += 30  # Within 2% below cutoff
    elif percentile_diff >= -5:
        score += 20  # Within 5% below cutoff
    elif percentile_diff >= -10:
        score += 10  # Within 10% below cutoff
    # else: score += 0
    
    # 2. CATEGORY MATCH (0-25 points)
    if student_category == college_category:
        score += 25  # Exact category match
    else:
        score += 5   # Different category but acceptable
    
    # 3. BRANCH MATCH (0-20 points)
    college_branch_lower = college_branch.lower()
    if normalized_branch in college_branch_lower or college_branch_lower in normalized_branch or \
       normalized_branch == college_branch_lower:
        score += 20  # Exact branch match
    else:
        score += 0   # Branch doesn't match
    
    # 4. CITY PREFERENCE (0-15 points)
    if student_city:  # Only score if user selected a city
        if student_city == college_city.lower():
            score += 15  # City match
        else:
            score += 0   # City doesn't match
    else:
        score += 15  # No city preference = no penalty
    
    return score

def recommend_colleges(student_percentile, category, branch, city, exam_type="MHT-CET"):
    
    normalized_branch = normalize_branch(branch)
    category = category.upper().strip()
    city = city.lower().strip() if city else ""
    exam_type = exam_type.upper().strip() if exam_type else "MHT-CET"
    
    # Fetch all colleges from MongoDB
    all_colleges = []
    try:
        for doc in colleges_col.find():
            all_colleges.append({
                "college": doc.get("college"),
                "branch": doc.get("branch"),
                "category": doc.get("category"),
                "cutoff": float(doc.get("cutoff_percentile", 0)),
                "city": doc.get("city", "").lower(),
                "exam_type": doc.get("exam_type", "MHT-CET").upper(),
                "_id": doc.get("_id")
            })
    except Exception as e:
        print(f"Error reading from MongoDB: {e}")
        return []
    
    # Score each college and filter by minimum criteria
    scored_colleges = []
    
    for college in all_colleges:
        college_branch = college["branch"].lower()
        college_category = college["category"].upper()
        college_cutoff = college["cutoff"]
        college_city = college["city"]
        
        # MINIMUM FILTER: Must have matching branch to be considered
        if not (normalized_branch in college_branch or college_branch in normalized_branch or 
                normalized_branch == college_branch):
            continue  # Skip colleges without matching branch
        
        # MINIMUM FILTER: Must match city if specified (case-insensitive substring match)
        if city and city not in college_city and college_city not in city:
            continue  # Skip colleges not in the preferred city

        # MINIMUM FILTER: Must match selected exam type
        if exam_type and college.get("exam_type", "MHT-CET") != exam_type:
            continue
        
        # Calculate match score
        score = calculate_match_score(
            student_percentile, category, normalized_branch, city,
            college, college_cutoff, college_category, college_branch, college_city, exam_type
        )
        
        # Skip colleges with very low scores (more than 15% below cutoff or rank far above cutoff)
        if exam_type == 'JEE ADVANCED':
            if student_percentile - college_cutoff > 700:
                continue
        else:
            if student_percentile - college_cutoff < -15:
                continue
        
        # Calculate admission chance
        chance = calculate_chance(student_percentile, college_cutoff, exam_type)
        
        scored_colleges.append({
            "college": college["college"],
            "branch": college["branch"],
            "category": college["category"],
            "cutoff": college_cutoff,
            "city": college_city,
            "exam_type": college["exam_type"],
            "chance": chance,
            "match_type": "exact" if category == college_category else "alternative_category",
            "match_score": score
        })
    
    # Sort by match score (descending), then by cutoff (descending)
    scored_colleges.sort(key=lambda x: (x["match_score"], x["cutoff"]), reverse=True)
    
    # Return top 25 results
    return scored_colleges[:25]
