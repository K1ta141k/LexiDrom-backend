"""
Text Comparison Service
Handles text comparison using Google's Gemma-3n model

Citation:
- Paper: "Gemma: Open Models Based on Gemini Research and Technology" (2024)
- Authors: Google DeepMind and Google Research
- DOI: arXiv:2403.08295
- Model: Gemma-3n (nano variant) for efficient text analysis and comparison
"""

import os
import google.generativeai as genai
from typing import List, Dict, Any, Tuple

class TextComparisonService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemma-3n-e4b-it')
        else:
            self.model = None
            print("⚠️ Google API key not found")
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.model is not None
    
    async def compare_texts(
        self,
        original_text: str,
        summary_text: str,
        reading_mode: str = "detailed"
    ) -> Tuple[int, List[str], List[str], List[str]]:
        """
        Compare original text with summary text
        Returns: (accuracy_score, correct_points, missed_points, wrong_points)
        """
        if not self.is_available():
            # Fallback to simple comparison
            return self._simple_comparison(original_text, summary_text)
        
        try:
            # Create prompt based on reading mode
            prompt = self._create_comparison_prompt(original_text, summary_text, reading_mode)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse the response
            return self._parse_comparison_response(response.text)
            
        except Exception as e:
            print(f"❌ Error in AI comparison: {e}")
            # Fallback to simple comparison
            return self._simple_comparison(original_text, summary_text)
    
    def _create_comparison_prompt(
        self,
        original_text: str,
        summary_text: str,
        reading_mode: str
    ) -> str:
        """Create the comparison prompt for the AI model"""
        
        # Reading mode descriptions
        mode_descriptions = {
            "skimming": "Quick overview focusing on main ideas and key points",
            "comprehension": "Understanding check and verification of key concepts",
            "study": "Educational focus with detailed analysis of learning objectives",
            "review": "Revision and retention focus with emphasis on important details",
            "summary": "Summary generation and evaluation with focus on conciseness",
            "detailed": "Comprehensive analysis of all content and details",
            "critical": "Analysis and evaluation of arguments and evidence",
            "comparison": "Compare multiple texts or versions with emphasis on differences"
        }
        
        mode_desc = mode_descriptions.get(reading_mode, mode_descriptions["detailed"])
        
        prompt = f"""
You are an expert text analyst. Compare the original text with the user's summary and provide a detailed analysis.


**Original Text**:
{original_text}

**User's Summary**:
{summary_text}

**Analysis Instructions**:
1. Evaluate how well the summary captures the key points from the original text
2. Provide an accuracy score from 0 to 100
3. Identify correctly captured points
4. Identify important points that were missed
5. Identify any incorrect or misleading information

**Response Format**:
Please respond in the following JSON format:

{{
    "accuracy_score": <0-100>,
    "correct_points": [
        "Point 1 description",
        "Point 2 description"
    ],
    "missed_points": [
        "Important point that was missed",
        "Another missed point"
    ],
    "wrong_points": [
        "Incorrect information in summary",
        "Misleading statement"
    ]
}}

**Guidelines**:
- Be objective and fair in your assessment
- Focus on the most important points for the given reading mode
- Provide specific, actionable feedback
- Consider the context and purpose of the reading mode
- Accuracy score should reflect overall quality and completeness
"""

        return prompt
    
    def _parse_comparison_response(self, response_text: str) -> Tuple[int, List[str], List[str], List[str]]:
        """Parse the AI response into structured data"""
        try:
            # Extract JSON from response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                accuracy_score = data.get("accuracy_score", 0)
                correct_points = data.get("correct_points", [])
                missed_points = data.get("missed_points", [])
                wrong_points = data.get("wrong_points", [])
                
                return accuracy_score, correct_points, missed_points, wrong_points
            else:
                # Fallback parsing
                return self._fallback_parsing(response_text)
                
        except Exception as e:
            print(f"❌ Error parsing AI response: {e}")
            return self._fallback_parsing(response_text)
    
    def _fallback_parsing(self, response_text: str) -> Tuple[int, List[str], List[str], List[str]]:
        """Fallback parsing when JSON parsing fails"""
        try:
            # Simple keyword-based parsing
            accuracy_score = 50  # Default score
            
            # Look for accuracy score
            import re
            score_match = re.search(r'accuracy[_\s]?score[:\s]*(\d+)', response_text, re.IGNORECASE)
            if score_match:
                accuracy_score = int(score_match.group(1))
            
            # Extract points based on keywords
            correct_points = []
            missed_points = []
            wrong_points = []
            
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if 'correct' in line.lower() or 'good' in line.lower() or 'accurate' in line.lower():
                    current_section = 'correct'
                elif 'missed' in line.lower() or 'missing' in line.lower():
                    current_section = 'missed'
                elif 'wrong' in line.lower() or 'incorrect' in line.lower() or 'error' in line.lower():
                    current_section = 'wrong'
                elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    point = line[1:].strip()
                    if point and current_section:
                        if current_section == 'correct':
                            correct_points.append(point)
                        elif current_section == 'missed':
                            missed_points.append(point)
                        elif current_section == 'wrong':
                            wrong_points.append(point)
            
            return accuracy_score, correct_points, missed_points, wrong_points
            
        except Exception as e:
            print(f"❌ Error in fallback parsing: {e}")
            return 50, [], [], []
    
    def _simple_comparison(
        self,
        original_text: str,
        summary_text: str
    ) -> Tuple[int, List[str], List[str], List[str]]:
        """Simple text comparison when AI is not available"""
        try:
            # Basic word overlap analysis
            original_words = set(original_text.lower().split())
            summary_words = set(summary_text.lower().split())
            
            # Calculate overlap
            overlap = len(original_words.intersection(summary_words))
            total_original = len(original_words)
            
            if total_original > 0:
                accuracy_score = min(100, int((overlap / total_original) * 100))
            else:
                accuracy_score = 50
            
            # Simple point extraction
            correct_points = ["Basic content overlap detected"]
            missed_points = ["Detailed analysis not available"]
            wrong_points = []
            
            return accuracy_score, correct_points, missed_points, wrong_points
            
        except Exception as e:
            print(f"❌ Error in simple comparison: {e}")
            return 50, [], [], [] 