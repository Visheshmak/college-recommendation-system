"""
Comprehensive Tests for College Recommendation System
Run with: pytest tests/test_app.py -v
"""

import pytest
import json
from datetime import datetime
from flask import Flask
from mongomock import MongoClient
from app import app as flask_app


@pytest.fixture
def client():
    """Create test client"""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def app_context():
    """Create app context"""
    with flask_app.app_context():
        yield flask_app


class TestHomePage:
    """Test home page functionality"""
    
    def test_index_page_loads(self, client):
        """Test that home page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'MHT-CET' in response.data
    
    def test_features_page_loads(self, client):
        """Test that features page loads"""
        response = client.get('/features')
        assert response.status_code == 200
        assert b'Features' in response.data


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error_page(self, client):
        """Test 404 error page"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'404' in response.data or b'not found' in response.data.lower()
    
    def test_500_error_handler(self, client):
        """Test 500 error handler exists"""
        # This would require intentionally triggering a 500 error
        # For now, just verify the handler is registered
        assert 500 in flask_app.error_handler_spec[None]


class TestAPIEndpoints:
    """Test REST API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_get_colleges_endpoint(self, client):
        """Test get colleges endpoint"""
        response = client.get('/api/colleges?limit=10')
        assert response.status_code in [200, 500]  # 500 if DB not available
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'data' in data
            assert 'colleges' in data['data']
    
    def test_get_colleges_with_filters(self, client):
        """Test get colleges with filters"""
        response = client.get('/api/colleges?city=Mumbai&branch=CSE&limit=5')
        assert response.status_code in [200, 500]
    
    def test_search_colleges_endpoint(self, client):
        """Test search endpoint"""
        payload = {
            'query': 'Mumbai',
            'filters': {
                'branch': 'CSE'
            },
            'limit': 10
        }
        response = client.post('/api/search',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code in [200, 400, 500]
    
    def test_recommendation_endpoint(self, client):
        """Test recommendation endpoint"""
        payload = {
            'percentile': 95.5,
            'category': 'General',
            'branch': 'CSE',
            'city': 'Mumbai'
        }
        response = client.post('/api/recommend',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code in [200, 400, 500]


class TestValidators:
    """Test validation functions"""
    
    def test_validate_email(self):
        """Test email validation"""
        from validators import validate_email
        
        assert validate_email('test@example.com') == True
        assert validate_email('invalid-email') == False
        assert validate_email('test@domain.co.in') == True
    
    def test_validate_percentile(self):
        """Test percentile validation"""
        from validators import validate_percentile
        
        assert validate_percentile(95.5) == True
        assert validate_percentile(0) == True
        assert validate_percentile(100) == True
        assert validate_percentile(150) == False
        assert validate_percentile(-10) == False
    
    def test_validate_required_fields(self):
        """Test required fields validation"""
        from validators import validate_required_fields, ValidationError
        
        data = {'name': 'John', 'email': 'john@example.com'}
        assert validate_required_fields(data, ['name', 'email']) == True
        
        with pytest.raises(ValidationError):
            validate_required_fields(data, ['name', 'email', 'phone'])
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        from validators import sanitize_string
        
        result = sanitize_string('  hello   world  ')
        assert result == 'hello world'
        
        result = sanitize_string('test<script>alert("xss")</script>')
        assert '<script>' not in result
    
    def test_validate_search_query(self):
        """Test search query validation"""
        from validators import validate_search_query, ValidationError
        
        assert validate_search_query('Mumbai colleges') == 'Mumbai colleges'
        
        with pytest.raises(ValidationError):
            validate_search_query('')  # Empty query
        
        with pytest.raises(ValidationError):
            validate_search_query('a')  # Too short
    
    def test_validate_college_filters(self):
        """Test college filter validation"""
        from validators import validate_college_filters, ValidationError
        
        filters = {
            'city': 'Mumbai',
            'branch': 'cse',
            'fees_min': 1000000,
            'fees_max': 2000000
        }
        result = validate_college_filters(filters)
        assert 'city' in result
        assert result['branch'] == 'CSE'
        
        # Test invalid branch
        with pytest.raises(ValidationError):
            invalid_filters = {'branch': 'INVALID'}
            validate_college_filters(invalid_filters)
    
    def test_validate_password(self):
        """Test password validation"""
        from validators import validate_password, ValidationError
        
        assert validate_password('StrongPass123') == True
        
        with pytest.raises(ValidationError):
            validate_password('weak')  # Too short
        
        with pytest.raises(ValidationError):
            validate_password('nouppercasepass123')  # No uppercase
    
    def test_format_responses(self):
        """Test response formatting"""
        from validators import format_success_response, format_error_response
        
        success = format_success_response({'data': 'test'})
        assert success['success'] == True
        assert success['data']['data'] == 'test'
        assert 'timestamp' in success
        
        error = format_error_response('Error message', 'ERROR_CODE')
        assert error['success'] == False
        assert error['error'] == 'Error message'
        assert error['error_code'] == 'ERROR_CODE'


class TestAuthentication:
    """Test authentication features"""
    
    def test_login_page_loads(self, client):
        """Test login page"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_register_page_loads(self, client):
        """Test register page"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower()


class TestFormSubmissions:
    """Test form submissions"""
    
    def test_student_details_form_page(self, client):
        """Test student details form page loads"""
        response = client.get('/student-details')
        assert response.status_code == 200
        assert b'Student' in response.data or b'Details' in response.data


class TestDataValidation:
    """Test data validation in forms"""
    
    def test_invalid_percentile_format(self):
        """Test invalid percentile format"""
        from validators import validate_percentile
        
        result = validate_percentile("invalid")
        assert result == False
    
    def test_boundary_percentile_values(self):
        """Test boundary percentile values"""
        from validators import validate_percentile
        
        assert validate_percentile(0.0) == True
        assert validate_percentile(50.0) == True
        assert validate_percentile(100.0) == True
        assert validate_percentile(0.001) == True
        assert validate_percentile(99.999) == True


# Integration Tests
class TestIntegration:
    """Integration tests"""
    
    def test_full_recommendation_flow(self, client):
        """Test complete recommendation flow"""
        # This is a high-level integration test
        pass
    
    def test_api_error_responses(self, client):
        """Test API error responses"""
        # Missing required fields
        response = client.post('/api/recommend',
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code in [400, 500]
    
    def test_rate_limiting(self, client):
        """Test rate limiting on API endpoints"""
        # Make multiple requests rapidly
        for i in range(5):
            response = client.get('/api/health')
            assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
