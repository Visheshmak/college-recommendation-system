"""
LLM Integration for College Chatbot
Supports OpenAI, Groq, and fallback to pattern matching
"""

import os
from dotenv import load_dotenv
import json

load_dotenv()

# Check which LLM provider to use
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()  # groq, openai, or ollama
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")  # Groq default


class LLMInterface:
    """Base LLM interface"""
    
    @staticmethod
    def get_response(user_input, context=""):
        raise NotImplementedError


class GroqLLM(LLMInterface):
    """Groq API integration (Free, Fast, No credit card)"""
    
    @staticmethod
    def get_response(user_input, context=""):
        """Get response from Groq API"""
        try:
            from groq import Groq
            
            client = Groq(api_key=LLM_API_KEY)
            
            system_prompt = """You are a helpful College Admission Assistant. You help students with:
- College information (fees, placements, cutoffs, hostels, academics)
- Admission process and eligibility
- Career guidance
- Available branches and specializations
- Campus facilities and student life

Provide accurate, concise, and helpful information. If you don't know something specific about a college, 
suggest they contact the college directly or check the official website. Keep responses under 300 words."""
            
            message = f"{context}\n\nStudent Question: {user_input}" if context else user_input
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                model=LLM_MODEL,
                max_tokens=500,
                temperature=0.7
            )
            
            response = chat_completion.choices[0].message.content
            print(f"[LLM] Using Groq API: {LLM_MODEL}")
            return response
            
        except ImportError:
            print("⚠️  Groq library not installed. Install: pip install groq")
            return None
        except Exception as e:
            print(f"⚠️  Groq API error: {e}")
            return None


class OpenAILLM(LLMInterface):
    """OpenAI API integration"""
    
    @staticmethod
    def get_response(user_input, context=""):
        """Get response from OpenAI API"""
        try:
            import openai
            
            openai.api_key = LLM_API_KEY
            
            system_prompt = """You are a helpful College Admission Assistant. You help students with:
- College information (fees, placements, cutoffs, hostels, academics)
- Admission process and eligibility
- Career guidance

Provide accurate, concise, and helpful information. Keep responses under 300 words."""
            
            message = f"{context}\n\nStudent Question: {user_input}" if context else user_input
            
            response = openai.ChatCompletion.create(
                model=LLM_MODEL or "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            print(f"[LLM] Using OpenAI: {LLM_MODEL}")
            return result
            
        except ImportError:
            print("⚠️  OpenAI library not installed. Install: pip install openai")
            return None
        except Exception as e:
            print(f"⚠️  OpenAI API error: {e}")
            return None


class OllamaLLM(LLMInterface):
    """Local Ollama integration (Free, offline)"""
    
    @staticmethod
    def get_response(user_input, context=""):
        """Get response from local Ollama instance"""
        try:
            import requests
            
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
            model = LLM_MODEL or "mistral"
            
            system_prompt = """You are a helpful College Admission Assistant."""
            message = f"{context}\n\n{user_input}" if context else user_input
            
            response = requests.post(
                ollama_url,
                json={
                    "model": model,
                    "prompt": f"{system_prompt}\n{message}",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                print(f"[LLM] Using Ollama: {model}")
                return result
            else:
                print(f"⚠️  Ollama error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️  Ollama error: {e}")
            return None


def get_llm_provider():
    """Get configured LLM provider"""
    
    if not LLM_API_KEY and LLM_PROVIDER != "ollama":
        print("⚠️  LLM_API_KEY not set. Using pattern matching fallback.")
        return None
    
    if LLM_PROVIDER == "groq":
        return GroqLLM()
    elif LLM_PROVIDER == "openai":
        return OpenAILLM()
    elif LLM_PROVIDER == "ollama":
        return OllamaLLM()
    else:
        print(f"⚠️  Unknown LLM provider: {LLM_PROVIDER}")
        return None


def get_llm_response(user_input, context="", use_fallback=True):
    """
    Get response from LLM with fallback to pattern matching
    
    Args:
        user_input: Student's question
        context: Additional context about college (optional)
        use_fallback: Use pattern matching if LLM fails
    
    Returns:
        Response string
    """
    
    try:
        llm = get_llm_provider()
        
        if llm:
            response = llm.get_response(user_input, context)
            if response:
                return response
    except Exception as e:
        print(f"⚠️  LLM error: {e}")
    
    # Fallback to pattern matching if LLM fails or not configured
    if use_fallback:
        print("[INFO] Falling back to pattern matching...")
        from chatbot_logic import get_response
        from mongo_db import intents_col
        
        intents = list(intents_col.find({"type": "college_qa"}))
        return get_response(user_input, intents)
    
    return "I couldn't generate a response. Please try a different question."


# Test function
def test_llm():
    """Test LLM configuration"""
    print("\n🧪 Testing LLM Configuration\n")
    
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"LLM Model: {LLM_MODEL}")
    print(f"API Key Set: {'Yes' if LLM_API_KEY else 'No'}")
    
    test_question = "What are the admission requirements for engineering?"
    print(f"\nTest Question: {test_question}\n")
    
    response = get_llm_response(test_question)
    print(f"\nResponse:\n{response}\n")


if __name__ == "__main__":
    test_llm()
