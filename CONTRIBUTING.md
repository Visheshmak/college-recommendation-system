# Contributing to College Recommendation System

First off, thank you for considering contributing to the College Recommendation System! It's people like you that make this system such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check if the bug has already been reported. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**
* **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and explain the expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python/JavaScript style guides
* Include appropriate test cases
* Document new code with docstrings
* End all files with a newline

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- MongoDB Atlas account

### Local Environment Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/yourusername/college-recommendation-system.git
cd college-recommendation-system
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Mac/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Create .env file**
```bash
cp .env.example .env
# Edit .env with your local settings
```

5. **Run tests**
```bash
pytest tests/ -v
```

6. **Start development server**
```bash
python app.py
```

## Style Guides

### Python Style Guide

* Use PEP 8 style guide
* Use meaningful variable names
* Add docstrings to all functions and classes
* Keep functions small and focused
* Use type hints where applicable

**Example:**

```python
def get_college_recommendations(percentile: float, category: str, 
                               branch: str) -> list:
    """
    Get college recommendations based on student criteria.
    
    Args:
        percentile (float): Student's exam percentile
        category (str): Student's category (General, OBC, SC, ST)
        branch (str): Preferred engineering branch
        
    Returns:
        list: List of recommended colleges
    """
    pass
```

### HTML/CSS Style Guide

* Use semantic HTML tags
* Use consistent indentation (2 or 4 spaces)
* Use meaningful class and ID names
* Keep CSS organized with comments

### Commit Messages

* Use present tense ("Add feature" not "Added feature")
* Use imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests generously after the first line

**Example:**
```
Add advanced search filters for colleges

- Add filter by fees range
- Add filter by placement rate
- Add filter by city

Closes #123
```

### Branch Naming

* Feature branch: `feature/short-description`
* Bug fix branch: `fix/short-description`
* Documentation: `docs/short-description`
* Refactoring: `refactor/short-description`

**Example:**
```
feature/save-colleges
fix/button-click-issue
docs/api-documentation
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_recommender.py -v

# Run with coverage
pytest tests/ --cov=college_recommendation_chatbot --cov-report=html
```

### Writing Tests

* Write tests for new features
* Write tests for bug fixes
* Aim for >80% code coverage
* Use meaningful test names

**Example:**

```python
def test_get_college_recommendations_returns_list():
    """Test that recommendations returns a list"""
    recommendations = get_college_recommendations(95.5, "General", "CSE")
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

def test_get_college_recommendations_invalid_percentile():
    """Test that invalid percentile raises ValueError"""
    with pytest.raises(ValueError):
        get_college_recommendations(150, "General", "CSE")
```

## Documentation

* Update README.md for new features
* Add docstrings to all functions
* Update API documentation for new endpoints
* Keep CHANGELOG.md updated

## Questions or Need Help?

* Check the existing documentation
* Open a GitHub issue with tag [`question`]
* Join our community discussions

## Recognition

Contributors will be recognized in:
* README.md contributors section
* Release notes
* Project discussions

Thank you for contributing! ❤️
