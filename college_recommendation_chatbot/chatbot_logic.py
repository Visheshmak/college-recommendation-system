import re
from difflib import SequenceMatcher
import os
from dotenv import load_dotenv

load_dotenv()

USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"


def preprocess(text):
    """Preprocess text: lowercase and remove special characters"""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


def calculate_similarity(user_input, pattern):
    """
    Calculate similarity between user input and pattern using sequence matching
    Returns a score between 0 and 1
    """
    return SequenceMatcher(None, user_input, pattern).ratio()


def keyword_match_score(user_input_words, pattern_words):
    """
    Calculate keyword matching score
    Returns score between 0 and len(pattern_words)
    """
    score = 0
    for word in pattern_words:
        if word in user_input_words:
            score += 1
    
    # Bonus if all pattern words are in user input
    if score == len(pattern_words) and len(pattern_words) > 2:
        score += 2
    
    return score


def get_response_from_patterns(user_input, intents):
    """
    Get response using traditional pattern matching
    """
    if not user_input or not intents:
        return None
    
    user_input_clean = preprocess(user_input)
    user_input_words = user_input_clean.split()
    
    best_match = None
    highest_score = 0
    match_details = []
    
    for intent in intents:
        pattern = preprocess(intent.get("pattern", ""))
        pattern_words = pattern.split()
        
        # Skip empty patterns
        if not pattern or not pattern_words:
            continue
        
        # Calculate composite score
        score = 0
        
        # 1. Keyword matching (0-10 points)
        keyword_score = keyword_match_score(user_input_words, pattern_words)
        score += min(keyword_score, 10)
        
        # 2. Sequence similarity (0-10 points)
        similarity = calculate_similarity(user_input_clean, pattern)
        score += similarity * 10
        
        # 3. Exact word match bonus (0-5 points)
        exact_match_count = sum(1 for word in pattern_words if word == user_input_clean or f" {word} " in f" {user_input_clean} ")
        score += exact_match_count * 2
        
        match_details.append({
            'pattern': pattern,
            'response': intent.get("response", ""),
            'score': score,
            'category': intent.get("category", "general")
        })
    
    if match_details:
        # Sort by score descending
        match_details.sort(key=lambda x: x['score'], reverse=True)
        
        # Get best match
        best = match_details[0]
        
        # Only return if score is reasonable (threshold: 2.5)
        if best['score'] >= 2.5:
            best_match = best['response']
            highest_score = best['score']
    
    return best_match


def get_response(user_input, intents):
    """
    Get response - Uses LLM if enabled, falls back to pattern matching
    """
    
    # Try LLM first if enabled
    if USE_LLM:
        try:
            from llm_integration import get_llm_response
            response = get_llm_response(user_input, use_fallback=True)
            if response:
                return response
        except Exception as e:
            print(f"⚠️  LLM error, falling back to patterns: {e}")
    
    # Use pattern matching
    response = get_response_from_patterns(user_input, intents)
    
    if response:
        return response
    
    # Default responses if no match found
    default_responses = [
        "I'm not sure about that. Try asking about: fees, placements, hostel, admissions, academics, campus, or location.",
        "Could you rephrase your question? I can help with college-related questions about fees, placements, admissions, and more.",
        "I didn't quite understand that. What would you like to know about college - fees, placements, hostel, or admissions?",
        "For more specific information, please ask about: courses, internships, facilities, or career prospects."
    ]
    
    import random
    return random.choice(default_responses)
