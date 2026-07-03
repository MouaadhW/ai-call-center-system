import json
import random
from loguru import logger
from agent.intentclassifier import IntentClassifier
from agent.knowledgebase import KnowledgeBase
from db.database import SessionLocal
from db.models import Customer, Ticket
import config
from datetime import datetime

try:
    import ollama
    OLLAMAAVAILABLE = True
except ImportError:
    OLLAMAAVAILABLE = False
    logger.warning("Ollama not available, using rule-based responses")

class AIAgent:
    """Enhanced AI agent with smarter, more interactive conversation handling"""
    
    def init(self):
        self.intentclassifier = IntentClassifier()
        self.knowledgebase = KnowledgeBase()
        self.conversationstate = {}
        
        if OLLAMAAVAILABLE and config.LLMPROVIDER == "ollama":
            self.usellm = True
            logger.info(f"AI Agent initialized with LLM: {config.LLMMODEL}")
        else:
            self.usellm = False
            logger.info("AI Agent initialized with rule-based system")
    
    def getgreeting(self):
        """Get varied, natural greeting message"""
        greetings = [
            f"Hello! Thanks for calling {config.COMPANYNAME}. I'm your AI assistant. How can I help you today?",
            f"Hi there! Welcome to {config.COMPANYNAME}. What brings you here today?",
            f"Good day! I'm here to assist you with {config.COMPANYNAME}. What can I do for you?",
            f"Hello! I'm your virtual assistant at {config.COMPANYNAME}. How may I help you?",
            f"Hi! Thanks for reaching out to {config.COMPANYNAME}. What can I assist you with?"
        ]
        return random.choice(greetings)
    
    async def processinput(self, userinput, conversationhistory, callid=None):
        """
        ENHANCED: Process user input with smarter intelligence and natural responses
        
        Args:
            userinput: User's spoken text
            conversationhistory: List of conversation messages
            callid: Current call ID
            
        Returns:
            str: AI response
        """
        try:
            # Ensure we always have a callid for state tracking
            if callid is None:
                callid = "websession"

            # Classify intent
            intent = self.intentclassifier.classify(userinput)
            logger.info(f"[Call {callid}] Intent: {intent} | Input: {userinput[:50]}...")
            
            # Initialize or update conversation state
            if callid not in self.conversationstate:
                self.conversationstate[callid] = {
                    "intent": intent,
                    "customerid": None,
                    "verified": False,
                    "datacollected": {},
                    "retrycount": 0,
                    "awaitingcustomerid": False,
                    "lastquestion": None,
                    "conversationturns": 0
                }
            else:
                self.conversationstate[callid]["intent"] = intent
            
            state = self.conversationstate[callid]
            state["conversationturns"] += 1
            
            # ENHANCED: Better customer ID extraction with multiple patterns
            import re
            idpatterns = 
                r'\b(\d{1,6})\b',  # Any 1-6 digit number
                r'(?:id|number|account)[\s:',
                r'(?:it\'?s?|is)\s:',
                r'customer\s:',
                r'my\s:\s:?\s:',
            ]
            
            for pattern in idpatterns:
                match = re.search(pattern, userinput, re.IGNORECASE)
                if match:
                    potentialid = match.group(1)
                    customer = self.getcustomer(potentialid)
                    if customer:
                        state["customerid"] = potentialid
                        state["verified"] = True
                        state["awaitingcustomerid"] = False
                        logger.info(f"[Call {callid}] Customer {potentialid} ({customer.name}) verified")
                        break
            
            # Get customer info if verified
            customer = None
            if state.get("customerid"):
                customer = self.getcustomer(state["customerid"])
            
            # Route to enhanced handlers
            if intent == "billing":
                return await self.handlebillingenhanced(userinput, callid, conversationhistory, customer)
            
            elif intent == "technicalsupport":
                return await self.handletechnicalsupportenhanced(userinput, callid, conversationhistory, customer)
            
            elif intent == "accountinfo":
                return await self.handleaccountinfoenhanced(userinput, callid, conversationhistory, customer)
            
            elif intent == "newservice":
                return await self.handlenewserviceenhanced(userinput, callid, conversationhistory)
            
            elif intent == "greeting":
                return await self.handlegreetingenhanced(userinput, callid, conversationhistory)
            
            else:
                # Use smart response for all other queries
                return await self.getsmartresponse(userinput, conversationhistory, callid, customer, intent)
                
        except Exception as e:
            logger.error(f"[Call {callid}] Error processing input: {e}")
            
            # Smart error handling
            if callid and callid in self.conversationstate:
                state = self.conversationstate[callid]
                state["retrycount"] = state.get("retrycount", 0) + 1
                
                if state["retrycount"] < 3:
                    errorresponses = [
                        "I apologize, could you please repeat that?",
                        "Sorry, I didn't quite catch that. Could you say it again?",
                        "Pardon me, could you rephrase that?",
                        "I'm having trouble understanding. Could you try again?"
                    ]
                    return random.choice(errorresponses)
                else:
                    return "I'm having difficulty understanding. Let me connect you with a specialist who can better assist you."
            
            return "I apologize, I'm having trouble processing your request. Could you please try again?"
    
    async def handlegreetingenhanced(self, userinput, callid, conversationhistory):
        """Handle greetings with natural, varied responses"""
        responses = [
            "Hello! I'm here to help. What can I assist you with today?",
            "Hi there! How can I help you?",
            "Good day! What brings you here today?",
            "Hello! What can I do for you?",
            "Hi! How may I assist you today?"
        ]
        return random.choice(responses)
    
    async def handlebillingenhanced(self, userinput, callid, conversationhistory, customer=None):
        """ENHANCED: Handle billing with smarter, more natural responses"""
        state = self.conversationstate[callid]
        
        # Check if customer is verified
        if not state["verified"]:
            if state.get("awaitingcustomerid"):
                # Extract customer ID from input
                customerid = self.extractcustomerid(userinput)
                if customerid:
                    customer = self.getcustomer(customerid)
                    if customer:
                        state["customerid"] = customerid
                        state["verified"] = True
                        state["awaitingcustomerid"] = False
                        
                        # Provide billing info immediately with natural language
                        responses = [
                            f"Perfect! I found your account, {customer.name}. Your current balance is ${customer.balance:.2f} on the {customer.plan} plan. Would you like to make a payment?",
                            f"Thanks, {customer.name}! Your balance is ${customer.balance:.2f} and you're on our {customer.plan} plan. Need help with anything else?",
                            f"Got it! {customer.name}, you have a balance of ${customer.balance:.2f} on the {customer.plan} plan. What would you like to do?",
                        ]
                        return random.choice(responses)
                    else:
                        return f"I couldn't find customer ID {customerid} in our system. Could you double-check that number?"
                else:
                    return "I didn't catch your customer ID. Could you say it again, please?"
            else:
                state["awaitingcustomerid"] = True
                askidresponses = [
                    "I'd be happy to help with your billing. Can you provide your customer ID?",
                    "Sure! To check your bill, I'll need your customer ID. What is it?",
                    "Let me pull up your billing. What's your customer ID?",
                ]
                return random.choice(askidresponses)
        else:
            # Customer already verified
            if not customer:
                customer = self.getcustomer(state["customerid"])
            
            if not customer:
                state["verified"] = False
                return "I'm having trouble accessing your account. Could you provide your customer ID again?"
            
            # Provide billing info with varied responses
            responses = [
                f"{customer.name}, your balance is ${customer.balance:.2f} on the {customer.plan} plan. Need anything else?",
                f"Your current balance is ${customer.balance:.2f}, {customer.name}. You're on our {customer.plan} plan. Would you like to make a payment?",
                f"I see your balance is ${customer.balance:.2f} for the {customer.plan} plan. How can I help with that?",
            ]
            return random.choice(responses)
    
    async def handletechnicalsupportenhanced(self, userinput, callid, conversationhistory, customer=None):
        """ENHANCED: Handle technical support with empathy and efficiency"""
        state = self.conversationstate[callid]
        
        if not state["verified"]:
            if state.get("awaitingcustomerid"):
                customerid = self.extractcustomerid(userinput)
                if customerid:
                    customer = self.getcustomer(customerid)
                    if customer:
                        state["customerid"] = customerid
                        state["verified"] = True
                        state["awaitingcustomerid"] = False
                        
                        empathyresponses = [
                            f"Thanks, {customer.name}. I'm sorry you're having trouble. Can you describe the issue?",
                            f"Got it, {customer.name}. Tell me more about what's happening.",
                            f"Okay {customer.name}, I'm here to help. What's the problem you're experiencing?",
                        ]
                        return random.choice(empathyresponses)
                    else:
                        return f"I couldn't find customer ID {customerid}. Could you verify that number?"
                else:
                    return "I need your customer ID to help. What is it?"
            else:
                state["awaitingcustomerid"] = True
                supportaskresponses = [
                    "I'm sorry you're having issues. Let me help. What's your customer ID?",
                    "I'll get that fixed for you. First, can you give me your customer ID?",
                    "Let me assist with that. What's your customer ID?",
                ]
                return random.choice(supportaskresponses)
        else:
            # Create support ticket
            if not state.get("ticketcreated"):
                if not customer:
                    customer = self.getcustomer(state["customerid"])
                
                if not customer:
                    state["verified"] = False
                    return "I'm having trouble accessing your account. Customer ID again?"
                
                ticket = self.createticket(
                    customerid=state["customerid"],
                    issuetype="technicalsupport",
                    description=userinput
                )
                state["ticketcreated"] = True
                
                ticketresponses = [
                    f"I've created support ticket #{ticket.id} for you, {customer.name}. Our tech team will contact you within 24 hours. Anything else I can help with?",
                    f"Done! Ticket #{ticket.id} is created. You'll hear from our technicians within a day. Need anything else?",
                    f"All set, {customer.name}! Ticket #{ticket.id} is in the system. Our team will reach out within 24 hours. What else can I do for you?",
                ]
                return random.choice(ticketresponses)
            else:
                return "Your support ticket is already created. Our team will contact you soon. Anything else?"
    
    async def handleaccountinfoenhanced(self, userinput, callid, conversationhistory, customer=None):
        """ENHANCED: Handle account info with clear, helpful responses"""
        state = self.conversationstate[callid]
        
        if not state["verified"]:
            if state.get("awaitingcustomerid"):
                customerid = self.extractcustomerid(userinput)
                if customerid:
                    customer = self.getcustomer(customerid)
                    if customer:
                        state["customerid"] = customerid
                        state["verified"] = True
                        state["awaitingcustomerid"] = False
                        
                        inforesponses = [
                            f"Here's your info, {customer.name}: Phone {customer.phone}, {customer.plan} plan, status is {customer.status}. What else?",
                            f"Got it! {customer.name}, you're on the {customer.plan} plan, status {customer.status}. Phone on file is {customer.phone}. Need anything else?",
                            f"{customer.name}, your account shows: {customer.plan} plan, {customer.status} status, phone {customer.phone}. What would you like to know?",
                        ]
                        return random.choice(inforesponses)
                    else:
                        return f"Customer ID {customerid} not found. Can you check that number?"
                else:
                    return "I need your customer ID. What is it?"
            else:
                state["awaitingcustomerid"] = True
                return "I can help with your account info. What's your customer ID?"
        else:
            if not customer:
                customer = self.getcustomer(state["customerid"])
            
            if not customer:
                state["verified"] = False
                return "Having trouble with your account. Customer ID again?"
            
            accountresponses = [
                f"{customer.name}, you're on the {customer.plan} plan with {customer.status} status. Anything else?",
                f"Your account shows {customer.plan} plan, status is {customer.status}. What else can I help with?",
                f"Account status: {customer.status}, plan: {customer.plan}. Need anything else, {customer.name}?",
            ]
            return random.choice(accountresponses)
    
    async def handlenewserviceenhanced(self, userinput, callid, conversationhistory):
        """ENHANCED: Handle new service requests"""
        newserviceresponses = [
            "I'd love to help you with a new service! Let me transfer you to our sales team who can discuss plans and pricing.",
            "Great! Our sales team can help you with that. Let me connect you now.",
            "Perfect timing! I'll transfer you to sales to explore our service options.",
        ]
        return random.choice(newserviceresponses)
    
    async def getsmartresponse(self, userinput, conversationhistory, callid, customer=None, intent=None):
       """
        ENHANCED: Get intelligent, context-aware response
        """
        if not self.usellm:
            # Fallback to knowledge base
            response = self.knowledgebase.getresponse(userinput)
            return response or "I'm here to help! Could you tell me more about what you need?"
        
        try:
            state = self.conversationstate.get(callid, {})
            
            # Build comprehensive context
            contextparts = [
                f"You are a friendly, professional customer service agent for {config.COMPANYNAME}.",
                "You are speaking with a customer over the phone. Be conversational, natural, and helpful.",
                "Keep responses concise (1-2 sentences) since this is a voice conversation.",
                "Be empathetic and understanding. Use natural language, not robotic responses.",
                "Speak faster and more efficiently - get to the point quickly.",
            ]
            
            # Add customer context if available
            if customer:
                contextparts.append(
                    f"Customer Information: Name: {customer.name}, "
                    f"Plan: {customer.plan}, Balance: ${customer.balance:.2f}, Status: {customer.status}"
                )
            
            # Add intent context
            if intent:
                contextparts.append(f"Customer's intent appears to be: {intent.replace('', ' ')}")
            
            # Add state context
            if state.get("awaitingcustomerid"):
                contextparts.append("You are currently waiting for the customer to provide their customer ID.")
            
            # Add knowledge base context
            kbcontext = self.knowledgebase.getcontext()
            contextparts.append(kbcontext)
            
            # Build system message
            systemmessage = " ".join(contextparts)
            
            # Build messages with conversation history
            messages = [
                {
                    "role": "system",
                    "content": systemmessage
                }
            ]
            
            # Add conversation history (last 8 messages for context)
            for msg in conversationhistory[-8:]:
                messages.append(msg)
            
            # Add current user input
            messages.append({
                "role": "user",
                "content": userinput
            })
            
            logger.info(f"[Call {callid}] Calling LLM with {len(messages)} messages")
            
            # Get response from Ollama
            response = ollama.chat(
                model=config.LLMMODEL,
                messages=messages,
                options={
                    "temperature": 0.7,  # More creative/conversational
                    "topp": 0.9,
                    "numpredict": 120  # Shorter for faster speech
                }
            )
            
            airesponse = response['message']['content'].strip()
            logger.info(f"[Call {callid}] LLM response: {airesponse[:80]}...")
            
            return airesponse
            
        except Exception as e:
            logger.error(f"[Call {callid}] LLM error: {e}")
            # Fallback to knowledge base
            response = self.knowledgebase.getresponse(userinput)
            return response or "I apologize, I'm having trouble right now. Could you please repeat that?"
    
    def classifyintent(self, text):
        """Classify user intent"""
        return self.intentclassifier.classify(text)
    
    def shouldendconversation(self, conversationhistory):
        """Determine if conversation should end"""
        if len(conversationhistory) < 2:
            return False
        
        lastusermsg = None
        for msg in reversed(conversationhistory):
            if msg["role"] == "user":
                lastusermsg = msg["content"].lower()
                break
        
        if lastusermsg:
            endphrases = ["goodbye", "bye", "thank you", "thanks", "that's all", "nothing else", "no thanks"]
            return any(phrase in lastusermsg for phrase in endphrases)
        
        return False
    
    def extractcustomerid(self, text):
        """Extract customer ID from text with enhanced patterns"""
        import re
        
        # Enhanced patterns for better extraction
        patterns = 
            r'\b(\d{1,6})\b',  # Any 1-6 digit number
            r'(?:id|number|account)[\s:',
            r'(?:it\'?s?|is)\s:',
            r'customer\s:',
            r'my\s:\s:?\s:',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                customerid = match.group(1)
                # Verify it's a valid customer ID (1-6 digits)
                if 1 <= len(customerid) <= 6:
                    return customerid
        
        return None
    
    def getcustomer(self, customerid):
        """Get customer from database"""
        try:
            db = SessionLocal()
            customer = db.query(Customer).filter(Customer.id == int(customerid)).first()
            db.close()
            return customer
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            return None
    
    def createticket(self, customerid, issuetype, description):
        """Create support ticket"""
        try:
            db = SessionLocal()
            ticket = Ticket(
                customerid=customerid,
                type=issuetype,
                description=description,
                status="open",
                priority="normal",
                createdat=datetime.now()
            )
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            ticketid = ticket.id
            db.close()
            
            logger.info(f"Created ticket #{ticketid} for customer {customerid}")
            
            # Return a simple object with the ticket ID
            class TicketResult:
                def init(self, ticketid):
                    self.id = ticketid
            
            return TicketResult(ticketid)
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return None
    
    def getfarewell(self):
        """Get varied farewell message"""
        farewells = [
            f"Thank you for calling {config.COMPANYNAME}. Have a wonderful day!",
            f"It was my pleasure helping you. Take care!",
            f"Thanks for reaching out to {config.COMPANY_NAME}. Feel free to call anytime. Goodbye!",
            f"Great talking with you! Have an excellent day!",
            f"Thank you! Don't hesitate to call back if you need anything. Bye!"
        ]
        return random.choice(farewells)