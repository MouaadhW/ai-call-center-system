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
        Process user input and generate intelligent, human-like response using Ollama
        
        Args:
            user_input: User's spoken text
            conversation_history: List of conversation messages
            call_id: Current call ID
            
        Returns:
            str: AI response
        """
        try:
            # Ensure we always have a call_id for state tracking
            if call_id is None:
                call_id = "web_session"

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
                    "retry_count": 0,
                    "awaiting_customer_id": False
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
            
            # Handle structured tasks first (customer verification, ticket creation, etc.)
            # Then use Ollama to generate natural, conversational responses
            
            # Get customer info if verified
            customer = None
            if state.get("customer_id"):
                customer = self.get_customer(state["customer_id"])
            
            # Handle specific intents with structured logic + LLM enhancement
            if intent == "billing":
                return await self.handle_billing_smart(user_input, call_id, conversation_history, customer)
            
            elif intent == "technical_support":
                return await self.handle_technical_support_smart(user_input, call_id, conversation_history, customer)
            
            elif intent == "account_info":
                return await self.handle_account_info_smart(user_input, call_id, conversation_history, customer)
            
            elif intent == "new_service":
                return await self.handle_new_service_smart(user_input, call_id, conversation_history)
            
            else:
                # Use Ollama for all other queries (including greetings)
                return await self.get_smart_response(user_input, conversation_history, call_id, customer, intent)
                
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            # Better error response using LLM if available
            if self.use_llm:
                try:
                    return await self.get_llm_response(
                        "I'm having trouble understanding. Could you please rephrase that?",
                        conversation_history
                    )
                except:
                    pass
            
            # Fallback error response
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
        """Handle greeting intent (now uses LLM via get_smart_response)"""
        # This will be handled by get_smart_response in the main process_input method
        pass
    
    async def handle_billing_smart(self, user_input, call_id, conversation_history, customer=None):
        """Handle billing-related queries with smart LLM responses"""
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
                        
                        # ACTUALLY PROVIDE THE BILLING INFO - don't just ask Ollama
                        billing_info = (
                            f"Thanks, {customer.name}. I found your account. "
                            f"Your current balance is ${customer.balance:.2f} and your plan is {customer.plan}. "
                            "Would you like to make a payment or have any other questions?"
                        )
                        
                        # Use LLM to make it sound more natural if available
                        if self.use_llm:
                            try:
                                enhanced = await self.get_smart_response(
                                    f"Customer {customer.name} provided ID {customer_id}. Their balance is ${customer.balance:.2f} and plan is {customer.plan}. "
                                    "Generate a friendly, natural response sharing this exact information. Keep it concise.",
                                    conversation_history, call_id, customer, "billing"
                                )
                                return enhanced
                            except:
                                pass
                        
                        return billing_info
                    else:
                        return await self.get_smart_response(
                            f"I couldn't find customer ID {customer_id}. Generate a friendly response saying the account wasn't found and offer to create one.",
                            conversation_history, call_id, None, "billing"
                        )
                else:
                    state["awaiting_customer_id"] = True
                    return await self.get_smart_response(
                        "I didn't catch the customer ID. Ask them to provide it again in a friendly way.",
                        conversation_history, call_id, None, "billing"
                    )
            else:
                state["awaiting_customer_id"] = True
                # ACTUALLY ASK FOR ID - don't just delegate to Ollama
                response = "I'd be happy to help with your billing. Can you please provide your customer ID for verification?"
                
                # Enhance with LLM if available
                if self.use_llm:
                    try:
                        enhanced = await self.get_smart_response(
                            "Customer wants billing help. Ask for their customer ID in a friendly, natural way.",
                            conversation_history, call_id, None, "billing"
                        )
                        return enhanced
                    except:
                        pass
                
                return response
        else:
            # Customer already verified, provide billing info using LLM
            if not customer:
                customer = self.get_customer(state["customer_id"])
            
            if not customer:
                state["verified"] = False
                state["awaiting_customer_id"] = True
                return await self.get_smart_response(
                    "I couldn't find the customer account. Ask for their customer ID again.",
                    conversation_history, call_id, None, "billing"
                )
            
            # ACTUALLY PROVIDE THE INFO
            billing_info = (
                f"{customer.name}, your current balance is ${customer.balance:.2f} and your plan is {customer.plan}. "
                "Would you like to make a payment or have any other questions?"
            )
            
            # Enhance with LLM if available
            if self.use_llm:
                try:
                    enhanced = await self.get_smart_response(
                        f"Customer {customer.name} is asking about billing again. Their balance is ${customer.balance:.2f} and plan is {customer.plan}. "
                        "Generate a natural, friendly response sharing this information.",
                        conversation_history, call_id, customer, "billing"
                    )
                    return enhanced
                except:
                    pass
            
            return billing_info
    
    async def handle_technical_support_smart(self, user_input, call_id, conversation_history, customer=None):
        """Handle technical support requests with smart LLM responses"""
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
                        return await self.get_smart_response(
                            f"Customer {customer.name} provided their ID. Ask them to describe their technical issue in a friendly way.",
                            conversation_history, call_id, customer, "technical_support"
                        )
                    else:
                        return await self.get_smart_response(
                            f"Customer ID {customer_id} not found. Generate a friendly response saying the account wasn't found and offer to create one.",
                            conversation_history, call_id, None, "technical_support"
                        )
                else:
                    state["awaiting_customer_id"] = True
                    return await self.get_smart_response(
                        "Ask the customer for their customer ID in a friendly way.",
                        conversation_history, call_id, None, "technical_support"
                    )
            else:
                state["awaiting_customer_id"] = True
                return await self.get_smart_response(
                    "Customer needs technical support. Ask for their customer ID first in a friendly, natural way.",
                    conversation_history, call_id, None, "technical_support"
                )
        else:
            # Create support ticket
            if not state.get("ticket_created"):
                if not customer:
                    customer = self.get_customer(state["customer_id"])
                
                if not customer:
                    state["verified"] = False
                    state["awaiting_customer_id"] = True
                    return await self.get_smart_response(
                        "Customer account not found. Ask for their customer ID again.",
                        conversation_history, call_id, None, "technical_support"
                    )
                
                ticket = self.create_ticket(
                    customer_id=state["customer_id"],
                    issue_type="technical_support",
                    description=user_input
                )
                state["ticket_created"] = True
                
                return await self.get_smart_response(
                    f"I've created support ticket #{ticket.id} for customer {customer.name}. "
                    "Generate a friendly, natural response confirming the ticket was created and that our team will contact them within 24 hours. "
                    "Ask if there's anything else you can help with.",
                    conversation_history, call_id, customer, "technical_support"
                )
            else:
                return await self.get_smart_response(
                    "The ticket was already created. Generate a friendly reminder that the team will reach out soon and ask if there's anything else.",
                    conversation_history, call_id, customer, "technical_support"
                )
    
    async def handle_account_info_smart(self, user_input, call_id, conversation_history, customer=None):
        """Handle account information requests with smart LLM responses"""
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
                        
                        return await self.get_smart_response(
                            f"Customer {customer.name} provided their ID. Their account info: Phone: {customer.phone}, Plan: {customer.plan}, Status: {customer.status}. "
                            "Generate a friendly, natural response sharing this information and asking what else they'd like to know.",
                            conversation_history, call_id, customer, "account_info"
                        )
                    else:
                        return await self.get_smart_response(
                            f"Customer ID {customer_id} not found. Generate a friendly response saying the account wasn't found and offer to create one.",
                            conversation_history, call_id, None, "account_info"
                        )
                else:
                    state["awaiting_customer_id"] = True
                    return await self.get_smart_response(
                        "Ask the customer to provide their customer ID in a friendly way.",
                        conversation_history, call_id, None, "account_info"
                    )
            else:
                state["awaiting_customer_id"] = True
                return await self.get_smart_response(
                    "Customer wants account information. Ask for their customer ID in a friendly, natural way.",
                    conversation_history, call_id, None, "account_info"
                )
        else:
            if not customer:
                customer = self.get_customer(state["customer_id"])
            
            if not customer:
                state["verified"] = False
                state["awaiting_customer_id"] = True
                return await self.get_smart_response(
                    "Customer account not found. Ask for their customer ID again.",
                    conversation_history, call_id, None, "account_info"
                )
            
            return await self.get_smart_response(
                f"Customer {customer.name} is asking about their account. Status: {customer.status}, Plan: {customer.plan}. "
                "Generate a natural, friendly response sharing this information and asking if there's anything else.",
                conversation_history, call_id, customer, "account_info"
            )
    
    async def handle_new_service_smart(self, user_input, call_id, conversation_history):
        """Handle new service requests with smart LLM responses"""
        return await self.get_smart_response(
            "Customer is interested in a new service. Generate a friendly, natural response saying you'd be happy to help and that you'll transfer them to the sales team for available plans and pricing.",
            conversation_history, call_id, None, "new_service"
        )
    
    async def handle_general(self, user_input, conversation_history):
        """Handle general queries using LLM (now uses get_smart_response)"""
        return await self.get_smart_response(user_input, conversation_history, "web_session", None, None)
    
    async def get_smart_response(self, user_input, conversation_history, call_id, customer=None, intent=None):
        """
        Get intelligent, human-like response using Ollama with full context
        """
        if not self.use_llm:
            # Fallback to knowledge base
            response = self.knowledge_base.get_response(user_input)
            return response or "I'm here to help! Could you tell me more about what you need?"
        
        try:
            state = self.conversation_state.get(call_id, {})
            
            # Build comprehensive context
            context_parts = [
                f"You are a friendly, professional customer service agent for {config.COMPANY_NAME}.",
                "You are speaking with a customer over the phone. Be conversational, natural, and helpful.",
                "Keep responses concise (1-2 sentences) since this is a voice conversation.",
                "Be empathetic and understanding. Use natural language, not robotic responses.",
            ]
            
            # Add customer context if available
            if customer:
                context_parts.append(
                    f"Customer Information: Name: {customer.name}, "
                    f"Plan: {customer.plan}, Balance: ${customer.balance:.2f}, Status: {customer.status}"
                )
            
            # Add intent context
            if intent:
                context_parts.append(f"Customer's intent appears to be: {intent.replace('_', ' ')}")
            
            # Add state context
            if state.get("awaiting_customer_id"):
                context_parts.append("You are currently waiting for the customer to provide their customer ID.")
            
            # Add knowledge base context
            kb_context = self.knowledge_base.get_context()
            context_parts.append(kb_context)
            
            # Build system message
            system_message = " ".join(context_parts)
            
            # Build messages with full conversation history
            messages = [
                {
                    "role": "system",
                    "content": system_message
                }
            ]
            
            # Add conversation history (last 10 messages for better context)
            for msg in conversation_history[-10:]:
                messages.append(msg)
            
            # Add current user input
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            logger.info(f"Calling Ollama with {len(messages)} messages")
            
            # Get response from Ollama
            response = ollama.chat(
                model=config.LLM_MODEL,
                messages=messages,
                options={
                    "temperature": 0.7,  # More creative/conversational
                    "top_p": 0.9,
                    "num_predict": 150  # Limit response length for voice
                }
            )
            
            ai_response = response['message']['content'].strip()
            logger.info(f"Ollama response: {ai_response[:100]}...")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            # Fallback to knowledge base
            response = self.knowledge_base.get_response(user_input)
            return response or "I apologize, I'm having trouble right now. Could you please repeat that?"
    
    async def get_llm_response(self, user_input, conversation_history):
        """Get response from LLM (legacy method, now uses get_smart_response)"""
        return await self.get_smart_response(user_input, conversation_history, "web_session", None, None)
    
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
