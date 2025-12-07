import json
from loguru import logger
from agent.intent_classifier import IntentClassifier
from agent.knowledge_base import KnowledgeBase
from db.database import SessionLocal
from db.models import Customer, Ticket
import config
from datetime import datetime

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama not available, using rule-based responses")

class AIAgent:
    """Main AI agent for handling customer conversations"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.knowledge_base = KnowledgeBase()
        self.conversation_state = {}
        
        if OLLAMA_AVAILABLE and config.LLM_PROVIDER == "ollama":
            self.use_llm = True
            logger.info(f"AI Agent initialized with LLM: {config.LLM_MODEL}")
        else:
            self.use_llm = False
            logger.info("AI Agent initialized with rule-based system")
    
    def get_greeting(self):
        """Get initial greeting message"""
        greeting = self.knowledge_base.get_greeting()
        return greeting or f"Hello! Welcome to {config.COMPANY_NAME}. How can I help you today?"
    
    async def process_input(self, user_input, conversation_history, call_id=None):
        """
        Process user input and generate response with better error handling
        
        Args:
            user_input: User's spoken text
            conversation_history: List of conversation messages
            call_id: Current call ID
            
        Returns:
            str: AI response
        """
        try:
            # Classify intent
            intent = self.intent_classifier.classify(user_input)
            logger.info(f"Detected intent: {intent}")
            
            # Update conversation state
            if call_id not in self.conversation_state:
                self.conversation_state[call_id] = {
                    "intent": intent,
                    "customer_id": None,
                    "verified": False,
                    "data_collected": {},
                    "retry_count": 0
                }
            else:
                self.conversation_state[call_id]["intent"] = intent
            
            state = self.conversation_state[call_id]
            
            # Extract customer ID from input if present
            import re
            id_patterns = [
                r'\b(\d{1,6})\b',  # Any 1-6 digit number
                r'id\s(?:is\s)?(\d+)',
                r'number\s(?:is\s*)?(\d+)',
            ]
            
            for pattern in id_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    potential_id = match.group(1)
                    # Verify it's a valid customer
                    customer = self.get_customer(potential_id)
                    if customer:
                        state["customer_id"] = potential_id
                        state["verified"] = True
                        state["awaiting_customer_id"] = False
                        logger.info(f"Customer {potential_id} verified")
                        break
            
            # Route to appropriate handler
            if intent == "greeting":
                return self.handle_greeting()
            
            elif intent == "billing":
                return await self.handle_billing(user_input, call_id)
            
            elif intent == "technical_support":
                return await self.handle_technical_support(user_input, call_id)
            
            elif intent == "account_info":
                return await self.handle_account_info(user_input, call_id)
            
            elif intent == "new_service":
                return await self.handle_new_service(user_input, call_id)
            
            else:
                return await self.handle_general(user_input, conversation_history)
                
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            # Better error response
            if call_id and call_id in self.conversation_state:
                state = self.conversation_state[call_id]
                state["retry_count"] = state.get("retry_count", 0) + 1
                
                if state["retry_count"] < 3:
                    return "I apologize for the confusion. Could you please rephrase that?"
                else:
                    return "I'm having difficulty understanding. Let me connect you with a human agent who can better assist you."
            else:
                return "I apologize, I'm having trouble processing your request. Could you please try again?"
    
    def handle_greeting(self):
        """Handle greeting intent"""
        return "Hello! I'm here to help you. What can I assist you with today?"
    
    async def handle_billing(self, user_input, call_id):
        """Handle billing-related queries"""
        state = self.conversation_state[call_id]
        
        # Check if customer is verified
        if not state["verified"]:
            if state.get("awaiting_customer_id"):
                # Extract customer ID from input
                customer_id = self.extract_customer_id(user_input)
                if customer_id:
                    customer = self.get_customer(customer_id)
                    if customer:
                        state["customer_id"] = customer_id
                        state["verified"] = True
                        state["awaiting_customer_id"] = False
                        
                        # Return billing info
                        return f"Thank you for verifying. Your current balance is ${customer.balance:.2f}. Your plan is {customer.plan}. Is there anything else I can help you with?"
                    else:
                        return "I couldn't find that customer ID. Could you please provide it again?"
                else:
                    return "I didn't catch that. Could you please provide your customer ID?"
            else:
                state["awaiting_customer_id"] = True
                return "I'd be happy to help with your billing. Can you please provide your customer ID for verification?"
        else:
            # Customer already verified, provide billing info
            customer = self.get_customer(state["customer_id"])
            return f"Your current balance is ${customer.balance:.2f}. Would you like to make a payment or have any other questions?"
    
    async def handle_technical_support(self, user_input, call_id):
        """Handle technical support requests"""
        state = self.conversation_state[call_id]
        
        if not state["verified"]:
            if state.get("awaiting_customer_id"):
                customer_id = self.extract_customer_id(user_input)
                if customer_id:
                    customer = self.get_customer(customer_id)
                    if customer:
                        state["customer_id"] = customer_id
                        state["verified"] = True
                        state["awaiting_customer_id"] = False
                        return "Thank you. Can you please describe the technical issue you're experiencing?"
                    else:
                        return "I couldn't find that customer ID. Please try again."
                else:
                    return "Could you please provide your customer ID?"
            else:
                state["awaiting_customer_id"] = True
                return "I'll help you with that technical issue. First, can you provide your customer ID?"
        else:
            # Create support ticket
            if not state.get("ticket_created"):
                ticket = self.create_ticket(
                    customer_id=state["customer_id"],
                    issue_type="technical_support",
                    description=user_input
                )
                state["ticket_created"] = True
                
                return f"I've created a support ticket #{ticket.id} for your issue. Our technical team will contact you within 24 hours. Is there anything else I can help you with?"
            else:
                return "Your ticket has already been created. Our team will reach out soon. Anything else I can assist with?"
    
    async def handle_account_info(self, user_input, call_id):
        """Handle account information requests"""
        state = self.conversation_state[call_id]
        
        if not state["verified"]:
            if state.get("awaiting_customer_id"):
                customer_id = self.extract_customer_id(user_input)
                if customer_id:
                    customer = self.get_customer(customer_id)
                    if customer:
                        state["customer_id"] = customer_id
                        state["verified"] = True
                        state["awaiting_customer_id"] = False
                        
                        return f"Here's your account information: Name: {customer.name}, Phone: {customer.phone}, Plan: {customer.plan}, Status: {customer.status}. What else would you like to know?"
                    else:
                        return "Customer ID not found. Please try again."
                else:
                    return "Please provide your customer ID."
            else:
                state["awaiting_customer_id"] = True
                return "I can help you with your account information. Please provide your customer ID."
        else:
            customer = self.get_customer(state["customer_id"])
            return f"Your account status is {customer.status}. Your current plan is {customer.plan}. Anything else?"
    
    async def handle_new_service(self, user_input, call_id):
        """Handle new service requests"""
        return "I'd be happy to help you with a new service. Let me transfer you to our sales team who can assist you better with available plans and pricing."
    
    async def handle_general(self, user_input, conversation_history):
        """Handle general queries using LLM or knowledge base"""
        if self.use_llm:
            return await self.get_llm_response(user_input, conversation_history)
        else:
            # Use knowledge base
            response = self.knowledge_base.get_response(user_input)
            return response or "I'm not sure I understand. Could you please rephrase that or let me transfer you to a human agent?"
    
    async def get_llm_response(self, user_input, conversation_history):
        """Get response from LLM"""
        try:
            # Build context
            context = self.knowledge_base.get_context()
            
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": f"You are a helpful customer service agent for {config.COMPANY_NAME}. {context}"
                }
            ]
            
            # Add conversation history
            for msg in conversation_history[-6:]:  # Last 3 turns
                messages.append(msg)
            
            # Get response from Ollama
            response = ollama.chat(
                model=config.LLM_MODEL,
                messages=messages
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "I apologize, I'm having trouble right now. Let me transfer you to an agent."
    
    def classify_intent(self, text):
        """Classify user intent"""
        return self.intent_classifier.classify(text)
    
    def should_end_conversation(self, conversation_history):
        """Determine if conversation should end"""
        if len(conversation_history) < 2:
            return False
        
        last_user_msg = None
        for msg in reversed(conversation_history):
            if msg["role"] == "user":
                last_user_msg = msg["content"].lower()
                break
        
        if last_user_msg:
            end_phrases = ["goodbye", "bye", "thank you", "thanks", "that's all", "nothing else"]
            return any(phrase in last_user_msg for phrase in end_phrases)
        
        return False
    
    def extract_customer_id(self, text):
        """Extract customer ID from text"""
        import re
        
        # Look for patterns like "12345" or "customer id 12345"
        patterns = [
            r'\b(\d{4,6})\b',  # 4-6 digit number
            r'id\s+(\d+)',
            r'number\s+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_customer(self, customer_id):
        """Get customer from database"""
        try:
            db = SessionLocal()
            customer = db.query(Customer).filter(Customer.id == int(customer_id)).first()
            db.close()
            return customer
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            return None
    
    def create_ticket(self, customer_id, issue_type, description):
        """Create support ticket"""
        try:
            db = SessionLocal()
            ticket = Ticket(
                customer_id=customer_id,
                type=issue_type,
                description=description,
                status="open",
                created_at=datetime.now()
            )
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            db.close()
            
            logger.info(f"Created ticket #{ticket.id} for customer {customer_id}")
            return ticket
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return None
