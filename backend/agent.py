import google.generativeai as genai
import json
import re
from typing import Dict, List
from config import Config

class GeminiAnnotator:
    """
    AI Text Annotation Agent using Google Gemini API.
    Performs comprehensive text annotation including:
    - Named Entity Recognition (NER)
    - Sentiment Analysis
    - Keyword Extraction
    - Relationship Extraction
    """
    
    def __init__(self):
        """Initialize Gemini API with configuration."""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Use Gemini 2.5 Flash for fast responses and high free tier limits
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generation config for consistent JSON outputs
        self.generation_config = {
            'temperature': 0.1,  # Very low for consistent JSON
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8192,  # Larger to ensure complete responses
        }
    
    def annotate(self, text: str) -> Dict:
        """
        Main annotation function.
        
        Args:
            text: Input text to annotate
            
        Returns:
            Dictionary containing status and annotations
        """
        
        prompt = self._create_annotation_prompt(text)
        
        try:
            # Call Gemini API with generation config
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Extract text from response safely
            response_text = self._extract_response_text(response)
            
            if not response_text or len(response_text.strip()) == 0:
                print("Empty response from Gemini")
                return {
                    "status": "error",
                    "error": "Empty response from AI model",
                    "original_text": text
                }
            
            # Parse response
            annotations = self._parse_response(response_text)
            
            return {
                "status": "success",
                "original_text": text,
                "annotations": annotations,
                "model": "gemini-2.5-flash"
            }
        
        except Exception as e:
            print(f"Annotation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": f"Annotation failed: {str(e)}",
                "original_text": text
            }
    
    def _extract_response_text(self, response) -> str:
        """
        Safely extract text from Gemini response.
        
        Args:
            response: Gemini API response object
            
        Returns:
            Extracted text as string
        """
        try:
            # Try simple text accessor first
            return response.text
        except:
            # Fall back to parts accessor for complex responses
            try:
                if response.candidates:
                    parts = response.candidates[0].content.parts
                    text_parts = [part.text for part in parts if hasattr(part, 'text')]
                    return ''.join(text_parts)
                else:
                    return ""
            except Exception as e:
                print(f"Error extracting response text: {e}")
                return ""
    
    def _create_annotation_prompt(self, text: str) -> str:
        """Create detailed prompt for annotation task."""
        
        return f"""You are an expert text annotation AI. Analyze the text and provide structured annotations.

TEXT:
{text}

Extract these elements and return as valid JSON:

1. ENTITIES - Named entities in the text:
   - PERSON: People, patients (use "Patient" if unnamed)
   - ORGANIZATION: Hospitals, companies, departments
   - LOCATION: Places, cities, departments (e.g., "ED")
   - DATE: Specific dates and relative times
   - TIME: Time references
   - MONEY: Monetary amounts
   - PRODUCT: Medications, products, devices
   - EVENT: Named events

2. SENTIMENT - Overall sentiment of each sentence:
   - "positive", "negative", or "neutral"
   - confidence: 0.0 to 1.0

3. KEYWORDS - 5-8 most important terms:
   - Medical conditions, procedures, symptoms
   - importance: 0.0 to 1.0
   - category: "medical", "symptom", "treatment", "diagnostic", "general"

4. RELATIONSHIPS - Connections between entities:
   - patient-has-condition, patient-receives-treatment, etc.

Return ONLY valid JSON in this exact format:
{{
  "entities": {{"PERSON": [], "ORGANIZATION": [], "LOCATION": [], "DATE": [], "TIME": [], "MONEY": [], "PRODUCT": [], "EVENT": []}},
  "sentiment": [{{"sentence": "text", "sentiment": "neutral", "confidence": 0.8}}],
  "keywords": [{{"term": "keyword", "importance": 0.9, "category": "medical"}}],
  "relationships": [{{"subject": "Entity1", "relation": "has", "object": "Entity2"}}]
}}

CRITICAL: Return ONLY the JSON. No markdown. No explanation. Start with {{ and end with }}."""
    
    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse and clean Gemini response to extract JSON.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Parsed annotations dictionary
        """
        
        try:
            # Clean the response
            content = response_text.strip()
            
            # Remove markdown code blocks
            if "```json" in content:
                parts = content.split("```json")
                if len(parts) > 1:
                    content = parts[1].split("```")[0].strip()
            elif "```" in content:
                parts = content.split("```")
                if len(parts) >= 2:
                    content = parts[1].strip()
            
            # Find JSON boundaries
            start_idx = content.find('{')
            if start_idx == -1:
                print("No JSON object found in response")
                return self._get_default_annotations()
            
            # Find matching closing brace
            brace_count = 0
            end_idx = -1
            in_string = False
            escape_next = False
            
            for i in range(start_idx, len(content)):
                char = content[i]
                
                # Handle string escaping
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                
                # Track if we're inside a string
                if char == '"':
                    in_string = not in_string
                    continue
                
                # Only count braces outside strings
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
            
            if end_idx == -1:
                print("Warning: Incomplete JSON, attempting to repair...")
                # Get what we have and try to close it
                content = content[start_idx:]
                # Simple repair: close any open structures
                open_braces = content.count('{') - content.count('}')
                open_brackets = content.count('[') - content.count(']')
                if open_brackets > 0:
                    content += ']' * open_brackets
                if open_braces > 0:
                    content += '}' * open_braces
            else:
                content = content[start_idx:end_idx]
            
            # Clean up common JSON issues
            content = content.replace(',]', ']').replace(',}', '}')
            content = content.replace('\n', ' ').replace('\r', ' ')
            
            # Parse JSON
            annotations = json.loads(content)
            
            # Validate and fix structure
            annotations = self._validate_annotations(annotations)
            
            return annotations
        
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response snippet: {response_text[:300]}...")
            print(f"Attempted to parse: {content[:300] if 'content' in locals() else 'N/A'}...")
            return self._get_default_annotations()
        except Exception as e:
            print(f"Parse error: {e}")
            print(f"Response snippet: {response_text[:300]}...")
            return self._get_default_annotations()
    
    def _validate_annotations(self, annotations: Dict) -> Dict:
        """Ensure annotations have the correct structure."""
        
        default = self._get_default_annotations()
        
        # Ensure all required keys exist
        if "entities" not in annotations:
            annotations["entities"] = default["entities"]
        if "sentiment" not in annotations:
            annotations["sentiment"] = default["sentiment"]
        if "keywords" not in annotations:
            annotations["keywords"] = default["keywords"]
        if "relationships" not in annotations:
            annotations["relationships"] = default["relationships"]
        
        # Ensure entities has all entity types
        entity_types = ["PERSON", "ORGANIZATION", "LOCATION", "DATE", 
                       "TIME", "MONEY", "PRODUCT", "EVENT"]
        for entity_type in entity_types:
            if entity_type not in annotations["entities"]:
                annotations["entities"][entity_type] = []
        
        return annotations
    
    def _get_default_annotations(self) -> Dict:
        """Return default empty annotation structure."""
        
        return {
            "entities": {
                "PERSON": [],
                "ORGANIZATION": [],
                "LOCATION": [],
                "DATE": [],
                "TIME": [],
                "MONEY": [],
                "PRODUCT": [],
                "EVENT": []
            },
            "sentiment": [],
            "keywords": [],
            "relationships": []
        }


# Batch annotation support (optional - for multiple texts)
class BatchAnnotator:
    """Handle multiple text annotations efficiently."""
    
    def __init__(self):
        self.annotator = GeminiAnnotator()
    
    def annotate_batch(self, texts: List[str]) -> List[Dict]:
        """
        Annotate multiple texts.
        
        Args:
            texts: List of texts to annotate
            
        Returns:
            List of annotation results
        """
        results = []
        
        for idx, text in enumerate(texts):
            print(f"Annotating text {idx + 1}/{len(texts)}...")
            result = self.annotator.annotate(text)
            results.append(result)
        
        return results


# Conversational Agent for interactive refinement
class ConversationalAgent:
    """
    Agentic AI that can chat with users and refine annotations based on feedback.
    """
    
    def __init__(self):
        self.annotator = GeminiAnnotator()
        self.conversation_history = []
        self.current_text = None
        self.current_annotations = None
        
    def chat(self, user_message: str, text: str = None) -> Dict:
        """
        Process user message and return AI response.
        
        Args:
            user_message: User's chat message
            text: Optional text to annotate (if starting new annotation)
            
        Returns:
            Dictionary with AI response and updated annotations
        """
        try:
            # If new text provided, annotate it first
            if text and text != self.current_text:
                self.current_text = text
                annotation_result = self.annotator.annotate(text)
                self.current_annotations = annotation_result.get('annotations', {})
                
                # Add to conversation history
                self.conversation_history.append({
                    'role': 'user',
                    'content': f'Annotate this text: {text}'
                })
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': f'I have analyzed the text and extracted entities, sentiment, keywords, and relationships.'
                })
            
            # Build conversation prompt
            prompt = self._build_chat_prompt(user_message)
            
            # Get AI response
            response = self.annotator.model.generate_content(
                prompt,
                generation_config=self.annotator.generation_config
            )
            
            # Extract text safely
            ai_response = self.annotator._extract_response_text(response).strip()
            
            # Check if user wants to modify annotations
            modified_annotations = self._process_modification_request(user_message, ai_response)
            
            # Add to history
            self.conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': ai_response
            })
            
            # Keep history manageable (last 10 messages)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return {
                'status': 'success',
                'response': ai_response,
                'annotations': modified_annotations or self.current_annotations,
                'has_text': self.current_text is not None
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _build_chat_prompt(self, user_message: str) -> str:
        """Build prompt for chat interaction."""
        
        context = ""
        if self.current_text:
            context += f"\n\nCURRENT TEXT BEING ANALYZED:\n{self.current_text}\n"
        
        if self.current_annotations:
            context += f"\n\nCURRENT ANNOTATIONS:\n{json.dumps(self.current_annotations, indent=2)}\n"
        
        history = ""
        if self.conversation_history:
            history = "\n\nCONVERSATION HISTORY:\n"
            for msg in self.conversation_history[-6:]:  # Last 3 exchanges
                history += f"{msg['role'].upper()}: {msg['content']}\n"
        
        prompt = f"""You are an AI text annotation assistant. You help users analyze text and refine annotations based on their needs.

{context}
{history}

USER MESSAGE: {user_message}

INSTRUCTIONS:
1. If the user asks about the annotations, explain them clearly
2. If the user wants to modify/add/remove entities or annotations, acknowledge and explain what you would change
3. If the user asks questions about the text, answer based on your analysis
4. If the user wants to focus on specific aspects (e.g., only sentiment, only entities), guide them
5. Be conversational, helpful, and proactive in suggesting improvements

Respond naturally as a helpful AI assistant. Keep responses concise but informative."""

        return prompt
    
    def _process_modification_request(self, user_message: str, ai_response: str) -> Dict:
        """
        Check if user wants to modify annotations and apply changes.
        Returns modified annotations or None if no modification needed.
        """
        if not self.current_annotations:
            return None
        
        # Keywords that suggest modification
        modification_keywords = [
            'add', 'remove', 'delete', 'change', 'modify', 'update',
            'include', 'exclude', 'mark as', 'classify as', 'set'
        ]
        
        user_lower = user_message.lower()
        
        # Check if user wants modifications
        if not any(keyword in user_lower for keyword in modification_keywords):
            return None
        
        # For now, return None - in a full implementation, you would:
        # 1. Parse the user's request using NLP
        # 2. Apply specific modifications to self.current_annotations
        # 3. Return the modified annotations
        
        # This is a placeholder for future enhancement
        return None
    
    def reset(self):
        """Reset conversation and annotations."""
        self.conversation_history = []
        self.current_text = None
        self.current_annotations = None
