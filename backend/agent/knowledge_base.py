import json
from loguru import logger
import config
from pathlib import Path

class KnowledgeBase:
    """Company-specific knowledge base"""
    
    def __init__(self):
        self.kb_file = config.KB_FILE
        self.knowledge = self.load_knowledge()
    
    def load_knowledge(self):
        """Load knowledge base from JSON file"""
        try:
            if self.kb_file.exists():
                with open(self.kb_file, 'r') as f:
                    kb = json.load(f)
                logger.info("Knowledge base loaded successfully")
                return kb
            else:
                logger.warning("Knowledge base file not found, using defaults")
                return self.get_default_knowledge()
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return self.get_default_knowledge()
    
    def get_default_knowledge(self):
        """Get default knowledge base"""
        return {
            "greeting": "Hello! Welcome to AI Call Center. How can I help you today?",
            "company_info": {
                "name": "AI Call Center",
                "hours": "24/7",
                "support_email": "support@aicallcenter.com"
            },
            "intents": {
                "billing": {
                    "keywords": ["bill", "payment", "charge", "invoice"],
                    "response": "I can help you with billing. Let me check your account."
                },
                "technical_support": {
                    "keywords": ["issue", "problem", "not working", "broken"],
                    "response": "I'll help you resolve this technical issue."
                },
                "account_info": {
                    "keywords": ["account", "information", "details"],
                    "response": "I can provide your account information."
                }
            },
            "faq": {
                "What are your hours?": "We're available 24/7 to assist you.",
                "How do I pay my bill?": "You can pay your bill online, by phone, or by mail.",
                "How do I reset my password?": "You can reset your password on our website or I can help you with that."
            }
        }
    
    def get_greeting(self):
        """Get greeting message"""
        return self.knowledge.get("greeting", "Hello! How can I help you?")
    
    def get_response(self, query):
        """Get response for a query from knowledge base"""
        query_lower = query.lower()
        
        # Check FAQ
        faq = self.knowledge.get("faq", {})
        for question, answer in faq.items():
            if self._is_similar(query_lower, question.lower()):
                return answer
        
        # Check intents
        intents = self.knowledge.get("intents", {})
        for intent_name, intent_data in intents.items():
            keywords = intent_data.get("keywords", [])
            if any(keyword in query_lower for keyword in keywords):
                return intent_data.get("response", "")
        
        return None
    
    def get_context(self):
        """Get context for LLM"""
        company_info = self.knowledge.get("company_info", {})
        
        context = f"""
        Company: {company_info.get('name', 'AI Call Center')}
        Hours: {company_info.get('hours', '24/7')}
        Support Email: {company_info.get('support_email', 'support@aicallcenter.com')}
        
        You should:
        - Be helpful and professional
        - Verify customer identity before providing account information
        - Create support tickets for technical issues
        - Offer to transfer to human agent when needed
        - Keep responses concise and clear
        """
        
        return context
    
    def _is_similar(self, text1, text2, threshold=0.6):
        """Check if two texts are similar"""
        # Simple word overlap similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1 & words2)
        similarity = overlap / max(len(words1), len(words2))
        
        return similarity >= threshold
    
    def add_faq(self, question, answer):
        """Add FAQ entry"""
        if "faq" not in self.knowledge:
            self.knowledge["faq"] = {}
        
        self.knowledge["faq"][question] = answer
        self.save_knowledge()
    
    def save_knowledge(self):
        """Save knowledge base to file"""
        try:
            with open(self.kb_file, 'w') as f:
                json.dump(self.knowledge, f, indent=2)
            logger.info("Knowledge base saved successfully")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
