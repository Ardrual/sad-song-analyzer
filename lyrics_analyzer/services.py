import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

def configure_gemini():
    """Configure Gemini API with API key from settings"""
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in settings")
    genai.configure(api_key=api_key)

def analyze_lyrics_with_gemini(lyrics):
    """
    Analyze song lyrics using Google Gemini API
    Returns a dict with sad_score, tags, and description
    """
    try:
        configure_gemini()
        
        # Create the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
    except Exception as e:
        logger.error(f"Failed to configure Gemini or create model: {e}")
        return None
    
    try:
        
        # Craft the prompt for structured analysis
        prompt = f"""
        Analyze the following song lyrics for sadness and emotional content. 
        Please provide a response in the following JSON format:
        {{
            "sad_score": <number from 1.0-10.0 with one decimal place where 10.0 is extremely sad>,
            "tags": [<array of 2-3 relevant emotional tags>],
            "description": "<brief one sentence poetic description of the emotions conveyed in the song>"
        }}
        
        Consider factors like:
        - Themes of loss, heartbreak, loneliness, depression
        - Word choice and emotional language
        - Overall mood and tone
        - Imagery and metaphors used
        
        Song lyrics:
        {lyrics}
        
        Respond with ONLY the JSON object, no additional text.
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Validate response exists and has content
        if not response or not hasattr(response, 'text') or not response.text:
            logger.error("Empty or invalid response from Gemini API")
            return None
        
        # Parse the JSON response
        try:
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]   # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove trailing ```
            
            response_text = response_text.strip()
            result = json.loads(response_text)
            
            # Validate the response structure
            if not all(key in result for key in ['sad_score', 'tags', 'description']):
                logger.error(f"Missing required keys in response. Got keys: {list(result.keys())}")
                return None
            
            # Ensure sad_score is within valid range and format to one decimal place
            try:
                sad_score = float(result['sad_score'])
                if not 1.0 <= sad_score <= 10.0:
                    logger.error(f"Invalid sad_score: {sad_score}")
                    return None
                
                # Format to one decimal place
                sad_score = round(sad_score, 1)
            except (ValueError, TypeError) as e:
                logger.error(f"Error processing sad_score: {e}")
                return None
            
            # Ensure tags is a list
            if not isinstance(result['tags'], list):
                logger.error(f"Tags must be a list, got: {type(result['tags'])}")
                return None
            
            # Ensure description is a string
            if not isinstance(result['description'], str):
                logger.error(f"Description must be a string, got: {type(result['description'])}")
                return None
            
            return {
                'sad_score': sad_score,
                'tags': result['tags'],
                'description': result['description']
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response.text}")
            return None
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        # Return None to indicate API failure
        return None