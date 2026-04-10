"""
REST API Routes for College Recommendation System
Provides JSON endpoints for college data and operations
"""

from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from mongo_db import colleges_col, college_details_col, students_col, saved_colleges_col
from validators import (
    validate_search_query, validate_college_filters, rate_limit,
    format_success_response, format_error_response, ValidationError
)
import logging

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@api_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle validation errors"""
    return jsonify(format_error_response(str(error), "VALIDATION_ERROR")), 400


@api_bp.route('/colleges', methods=['GET'])
@rate_limit(max_requests=100, time_window=3600)
def get_colleges():
    """
    Get list of colleges with optional filters
    
    Query Parameters:
    - city: Filter by city
    - branch: Filter by branch
    - min_rating: Minimum rating (0-5)
    - limit: Number of results (default: 20, max: 100)
    - offset: Pagination offset (default: 0)
    
    Returns:
        JSON: List of colleges
    """
    try:
        # Get parameters
        city = request.args.get('city', '').strip()
        branch = request.args.get('branch', '').strip()
        min_rating = request.args.get('min_rating', type=float)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate limit
        limit = min(limit, 100)  # Max 100 results
        
        # Build query
        query = {}
        if city:
            query['city'] = {"$regex": city, "$options": "i"}
        if branch:
            query['branch'] = {"$regex": branch, "$options": "i"}
        if min_rating:
            query['rating'] = {"$gte": min_rating}
        
        # Fetch colleges
        colleges = list(colleges_col.find(query)
                       .skip(offset)
                       .limit(limit)
                       .sort("rating", -1))
        
        # Convert ObjectId to string
        for college in colleges:
            college['_id'] = str(college['_id'])
        
        return jsonify(format_success_response({
            'colleges': colleges,
            'total': colleges_col.count_documents(query),
            'limit': limit,
            'offset': offset
        }))
    
    except Exception as e:
        logger.error(f"Error fetching colleges: {str(e)}")
        return jsonify(format_error_response("Failed to fetch colleges", "DB_ERROR")), 500


@api_bp.route('/college/<college_name>', methods=['GET'])
@rate_limit()
def get_college_details(college_name):
    """
    Get detailed information about a specific college
    
    Parameters:
    - college_name: Name of the college
    
    Returns:
        JSON: Detailed college information
    """
    try:
        college = college_details_col.find_one(
            {"college": {"$regex": college_name, "$options": "i"}}
        )
        
        if not college:
            return jsonify(format_error_response("College not found", "NOT_FOUND")), 404
        
        college['_id'] = str(college['_id'])
        return jsonify(format_success_response(college))
    
    except Exception as e:
        logger.error(f"Error fetching college details: {str(e)}")
        return jsonify(format_error_response("Failed to fetch college details", "DB_ERROR")), 500


@api_bp.route('/search', methods=['POST'])
@rate_limit(max_requests=50)
def search_colleges():
    """
    Advanced search for colleges with multiple filters
    
    Request Body:
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
    
    Returns:
        JSON: Search results
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body must be JSON")
        
        # Validate search query
        query_str = data.get('query', '').strip()
        if query_str:
            query_str = validate_search_query(query_str)
        
        # Validate and sanitize filters
        filters = data.get('filters', {})
        if filters:
            filters = validate_college_filters(filters)
        
        # Build MongoDB query
        mongo_query = {}
        
        if query_str:
            mongo_query['$text'] = {"$search": query_str}
        
        if 'city' in filters:
            mongo_query['city'] = {"$regex": filters['city'], "$options": "i"}
        
        if 'branch' in filters:
            mongo_query['branch'] = filters['branch']
        
        if 'category' in filters:
            mongo_query['category'] = filters['category']
        
        if 'fees_min' in filters or 'fees_max' in filters:
            fees_query = {}
            if 'fees_min' in filters:
                fees_query['$gte'] = filters['fees_min']
            if 'fees_max' in filters:
                fees_query['$lte'] = filters['fees_max']
            mongo_query['fees'] = fees_query
        
        if 'rating_min' in filters:
            mongo_query['rating'] = {"$gte": filters['rating_min']}
        
        # Get pagination parameters
        limit = min(data.get('limit', 20), 100)
        offset = data.get('offset', 0)
        
        # Execute search
        results = list(colleges_col.find(mongo_query)
                      .skip(offset)
                      .limit(limit)
                      .sort("rating", -1))
        
        # Convert ObjectId
        for result in results:
            result['_id'] = str(result['_id'])
        
        return jsonify(format_success_response({
            'results': results,
            'total': colleges_col.count_documents(mongo_query),
            'limit': limit,
            'offset': offset,
            'query': query_str
        }))
    
    except ValidationError as e:
        return jsonify(format_error_response(str(e), "VALIDATION_ERROR")), 400
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify(format_error_response("Search failed", "SEARCH_ERROR")), 500


@api_bp.route('/recommend', methods=['POST'])
@rate_limit(max_requests=30)
def recommend():
    """
    Get college recommendations based on student criteria
    
    Request Body:
    {
        "percentile": 95.5,
        "category": "General",
        "branch": "CSE",
        "city": "Mumbai"
    }
    
    Returns:
        JSON: List of recommended colleges
    """
    try:
        from recommender import recommend_colleges
        
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body must be JSON")
        
        # Get required parameters
        percentile = data.get('percentile')
        category = data.get('category')
        branch = data.get('branch')
        city = data.get('city', '')
        
        # Validate
        if not all([percentile, category, branch]):
            raise ValidationError("percentile, category, and branch are required")
        
        if not isinstance(percentile, (int, float)) or not (0 <= percentile <= 100):
            raise ValidationError("percentile must be between 0 and 100")
        
        # Get recommendations
        recommendations = recommend_colleges(percentile, category, branch, city)
        
        return jsonify(format_success_response({
            'recommendations': recommendations,
            'count': len(recommendations)
        }, message="Recommendations generated successfully"))
    
    except ValidationError as e:
        return jsonify(format_error_response(str(e), "VALIDATION_ERROR")), 400
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        return jsonify(format_error_response("Failed to generate recommendations", "RECOMMENDATION_ERROR")), 500


@api_bp.route('/saved-colleges', methods=['GET', 'POST'])
@rate_limit()
def saved_colleges():
    """
    Get or add saved colleges for authenticated user
    
    GET: Retrieve all saved colleges
    POST: Save a new college
    
    POST Request Body:
    {
        "college_id": "college_object_id"
    }
    """
    try:
        from flask_login import current_user, login_required
        
        if request.method == 'GET':
            # Get saved colleges for user
            if not current_user.is_authenticated:
                return jsonify(format_error_response("Authentication required", "AUTH_REQUIRED")), 401
            
            saved = list(saved_colleges_col.find({"user_id": current_user.id}))
            
            for item in saved:
                item['_id'] = str(item['_id'])
                item['college_id'] = str(item.get('college_id', ''))
            
            return jsonify(format_success_response({'saved_colleges': saved}))
        
        elif request.method == 'POST':
            # Add to saved colleges
            if not current_user.is_authenticated:
                return jsonify(format_error_response("Authentication required", "AUTH_REQUIRED")), 401
            
            data = request.get_json()
            college_id = data.get('college_id')
            
            if not college_id:
                raise ValidationError("college_id is required")
            
            # Check if already saved
            existing = saved_colleges_col.find_one({
                "user_id": current_user.id,
                "college_id": ObjectId(college_id)
            })
            
            if existing:
                return jsonify(format_error_response("College already saved", "ALREADY_SAVED")), 409
            
            # Save college
            saved_colleges_col.insert_one({
                "user_id": current_user.id,
                "college_id": ObjectId(college_id),
                "saved_at": datetime.now()
            })
            
            return jsonify(format_success_response(None, "College saved successfully")), 201
    
    except ValidationError as e:
        return jsonify(format_error_response(str(e), "VALIDATION_ERROR")), 400
    except Exception as e:
        logger.error(f"Saved colleges error: {str(e)}")
        return jsonify(format_error_response("Operation failed", "DB_ERROR")), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


from datetime import datetime
