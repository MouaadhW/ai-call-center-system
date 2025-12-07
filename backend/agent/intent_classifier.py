from loguru import logger
import re

class IntentClassifier:
    """Classify user intent from text"""
    
    def __init__(self):
        self.intent_keywords = {
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon"],
            "billing": ["bill", "payment", "charge", "invoice", "balance", "pay", "cost", "price"],
            "technical_support": ["not working", "broken", "slow", "issue", "problem", "error", "down", "internet", "connection", "wifi"],
            "account_info": ["account", "information", "details", "profile", "plan", "subscription"],
            "new_service": ["new", "activate", "sign up", "register", "order", "sim card", "service"],
            "cancellation": ["cancel", "terminate", "close account", "stop service"],
            "complaint": ["complain", "unhappy", "disappointed", "frustrated", "angry"],
        }
    
    def classify(self, text):
        """
        Classify intent from text
        
        Args:
            text: User input text
            
        Returns:
            str: Detected intent
        """
        text_lower = text.lower()
        
        # Score each intent
        scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[intent] = score
        
        # Return highest scoring intent
        if scores:
            best_intent = max(scores, key=scores.get)
            logger.debug(f"Intent scores: {scores}, selected: {best_intent}")
            return best_intent
        
        # Default to general if no match
        return "general"
    
    def get_confidence(self, text, intent):
        """Get confidence score for an intent"""
        text_lower = text.lower()
        keywords = self.intent_keywords.get(intent, [])
        
        if not keywords:
            return 0.0
        
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        confidence = matches / len(keywords)
        
        return min(confidence, 1.0)
