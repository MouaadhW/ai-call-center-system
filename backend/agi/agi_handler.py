import asyncio
import socket
from loguru import logger
from asr.whisper_engine import WhisperASR
from tts.tts_engine import PiperTTS
from agent.agent import AIAgent
from db.database import SessionLocal
from db.models import Call
import config
import numpy as np
from datetime import datetime

class AGIServer:
    """AGI Server to handle Asterisk calls"""
    
    def __init__(self, host="0.0.0.0", port=4573):
        self.host = host
        self.port = port
        self.asr = WhisperASR()
        self.tts = PiperTTS()
        self.agent = AIAgent()
        
    async def start(self):
        """Start the AGI server"""
        server = await asyncio.start_server(
            self.handle_call,
            self.host,
            self.port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f"AGI Server listening on {addr}")
        
        async with server:
            await server.serve_forever()
    
    async def handle_call(self, reader, writer):
        """Handle incoming AGI call"""
        call_start = datetime.now()
        call_id = None
        
        try:
            # Read AGI environment variables
            agi_env = await self.read_agi_env(reader)
            logger.info(f"New call from {agi_env.get('agi_callerid', 'Unknown')}")
            
            # Create call record
            db = SessionLocal()
            call = Call(
                caller_number=agi_env.get('agi_callerid', 'Unknown'),
                start_time=call_start,
                status='in_progress'
            )
            db.add(call)
            db.commit()
            call_id = call.id
            db.close()
            
            # Answer the call
            await self.agi_command(writer, reader, "ANSWER")
            await asyncio.sleep(1)
            
            # Start conversation
            await self.run_conversation(writer, reader, agi_env, call_id)
            
        except Exception as e:
            logger.error(f"Error handling call: {e}")
        finally:
            # Update call record
            if call_id:
                db = SessionLocal()
                call = db.query(Call).filter(Call.id == call_id).first()
                if call:
                    call.end_time = datetime.now()
                    call.duration = int((call.end_time - call.start_time).total_seconds())
                    call.status = 'completed'
                    db.commit()
                db.close()
            
            writer.close()
            await writer.wait_closed()
    
    async def read_agi_env(self, reader):
        """Read AGI environment variables"""
        env = {}
        while True:
            line = await reader.readline()
            line = line.decode('utf-8').strip()
            
            if not line:
                break
            
            if ':' in line:
                key, value = line.split(':', 1)
                env[key.strip()] = value.strip()
        
        return env
    
    async def agi_command(self, writer, reader, command):
        """Send AGI command and get response"""
        writer.write(f"{command}\n".encode('utf-8'))
        await writer.drain()
        
        response = await reader.readline()
        response = response.decode('utf-8').strip()
        
        logger.debug(f"AGI Command: {command} -> Response: {response}")
        return response
    
    async def run_conversation(self, writer, reader, agi_env, call_id):
        """Run the AI conversation loop"""
        conversation_history = []
        
        # Initial greeting
        greeting = self.agent.get_greeting()
        await self.speak(writer, reader, greeting)
        conversation_history.append({"role": "assistant", "content": greeting})
        
        # Conversation loop
        max_turns = 20
        for turn in range(max_turns):
            try:
                # Listen to user
                user_text = await self.listen(writer, reader)
                
                if not user_text or user_text.lower() in ['goodbye', 'bye', 'thank you']:
                    farewell = "Thank you for calling. Goodbye!"
                    await self.speak(writer, reader, farewell)
                    break
                
                logger.info(f"User said: {user_text}")
                conversation_history.append({"role": "user", "content": user_text})
                
                # Get AI response
                response = await self.agent.process_input(
                    user_text,
                    conversation_history,
                    call_id
                )
                
                logger.info(f"AI responds: {response}")
                conversation_history.append({"role": "assistant", "content": response})
                
                # Speak response
                await self.speak(writer, reader, response)
                
                # Check if conversation should end
                if self.agent.should_end_conversation(conversation_history):
                    break
                    
            except Exception as e:
                logger.error(f"Error in conversation turn {turn}: {e}")
                error_msg = "I'm sorry, I'm having trouble understanding. Let me transfer you to an agent."
                await self.speak(writer, reader, error_msg)
                break
        
        # Save transcript
        await self.save_transcript(call_id, conversation_history)
    
    async def listen(self, writer, reader, timeout=10):
        """Record audio and transcribe"""
        try:
            # Record audio file
            temp_file = f"/tmp/recording_{datetime.now().timestamp()}.wav"
            
            # AGI RECORD FILE command
            cmd = f"RECORD FILE {temp_file} wav # {timeout * 1000} BEEP"
            response = await self.agi_command(writer, reader, cmd)
            
            # Transcribe with Whisper
            text = self.asr.transcribe_file(temp_file)
            
            return text
            
        except Exception as e:
            logger.error(f"Error in listen: {e}")
            return ""
    
    async def speak(self, writer, reader, text):
        """Convert text to speech and play"""
        try:
            # Generate audio with TTS
            audio_file = self.tts.synthesize_to_file(text)
            
            # Play audio via AGI
            cmd = f"STREAM FILE {audio_file.replace('.wav', '')} #"
            await self.agi_command(writer, reader, cmd)
            
        except Exception as e:
            logger.error(f"Error in speak: {e}")
    
    async def save_transcript(self, call_id, conversation_history):
        """Save conversation transcript to database"""
        try:
            db = SessionLocal()
            call = db.query(Call).filter(Call.id == call_id).first()
            
            if call:
                transcript = "\n".join([
                    f"{msg['role'].upper()}: {msg['content']}"
                    for msg in conversation_history
                ])
                call.transcript = transcript
                
                # Extract intent from conversation
                if len(conversation_history) > 2:
                    user_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
                    call.intent = self.agent.classify_intent(" ".join(user_messages))
                
                db.commit()
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error saving transcript: {e}")
