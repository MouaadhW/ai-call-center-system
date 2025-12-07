from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import asyncio
import json
from datetime import datetime
from loguru import logger

sys.path.insert(0, os.path.dirname(__file__))

from agent.agent import AIAgent
from db.database import SessionLocal
from db.models import Call

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = AIAgent()

# Store active calls
active_calls = {}

html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Call Center - Production</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .status {
            padding: 20px;
            margin: 20px 0;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .status.ready { background: #e8f5e9; color: #2e7d32; }
        .status.listening { 
            background: #fff3e0; 
            color: #e65100;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .status.speaking { background: #e3f2fd; color: #1565c0; }
        .status.error { background: #ffebee; color: #c62828; }
        
        button {
            padding: 18px 50px;
            font-size: 18px;
            font-weight: 600;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        button:active { transform: scale(0.95); }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        #startBtn {
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
        }
        #startBtn:hover:not(:disabled) { 
            box-shadow: 0 6px 20px rgba(76,175,80,0.4); 
        }
        
        #stopBtn {
            background: linear-gradient(135deg, #f44336, #e53935);
            color: white;
            display: none;
        }
        #stopBtn:hover { box-shadow: 0 6px 20px rgba(244,67,54,0.4); }
        
        #transcript {
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 12px;
            min-height: 250px;
            max-height: 400px;
            overflow-y: auto;
            text-align: left;
        }
        .message {
            margin: 12px 0;
            padding: 12px;
            border-radius: 8px;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .agent {
            background: #f1f8e9;
            border-left: 4px solid #4caf50;
        }
        .message strong {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #666;
        }
        .instructions {
            background: #fff9c4;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 13px;
            text-align: left;
        }
        .instructions strong {
            display: block;
            margin-bottom: 8px;
            color: #f57c00;
        }
        .instructions ul {
            margin: 8px 0 0 20px;
        }
        .instructions li {
            margin: 4px 0;
        }
        .mic-test {
            margin: 15px 0;
            padding: 12px;
            background: #e1f5fe;
            border-radius: 8px;
            font-size: 13px;
        }
        .mic-level {
            height: 8px;
            background: #ddd;
            border-radius: 4px;
            margin-top: 8px;
            overflow: hidden;
        }
        .mic-level-bar {
            height: 100%;
            background: linear-gradient(90deg, #4caf50, #8bc34a);
            width: 0%;
            transition: width 0.1s;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 AI Call Center</h1>
        <p class="subtitle">Professional Voice Assistant</p>
        
        <div class="instructions">
            <strong>📱 How to use on iPhone:</strong>
            <ul>
                <li>Tap "Start Call" button</li>
                <li>Allow microphone when prompted</li>
                <li>Wait for AI greeting (listen carefully)</li>
                <li>Speak clearly after each AI response</li>
                <li>Say "goodbye" or "thank you" to end</li>
            </ul>
        </div>
        
        <div class="mic-test" id="micTest" style="display:none;">
            <div>🎙️ Microphone Level:</div>
            <div class="mic-level">
                <div class="mic-level-bar" id="micLevel"></div>
            </div>
        </div>
        
        <div id="status" class="status ready">Ready to start</div>
        <button id="startBtn">🎤 Start Call</button>
        <button id="stopBtn">📞 End Call</button>
        <div id="transcript"></div>
    </div>
    
    <script>
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const status = document.getElementById('status');
        const transcript = document.getElementById('transcript');
        const micTest = document.getElementById('micTest');
        const micLevel = document.getElementById('micLevel');
        
        let recognition;
        let synthesis = window.speechSynthesis;
        let ws;
        let isListening = false;
        let audioContext;
        let microphone;
        let analyser;
        let silenceTimeout;
        let lastSpeechTime = Date.now();
        let callId = null;
        
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            status.textContent = '❌ Speech not supported. Use Safari on iOS 14.5+';
            status.className = 'status error';
            startBtn.disabled = true;
        }
        
        // Test microphone access
        async function testMicrophone() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                // Setup audio context for level monitoring
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                microphone = audioContext.createMediaStreamSource(stream);
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 256;
                microphone.connect(analyser);
                
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                
                function updateLevel() {
                    if (!isListening) return;
                    analyser.getByteFrequencyData(dataArray);
                    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
                    const level = Math.min(100, (average / 128) * 100);
                    micLevel.style.width = level + '%';
                    requestAnimationFrame(updateLevel);
                }
                
                micTest.style.display = 'block';
                updateLevel();
                
                return true;
            } catch (err) {
                status.textContent = '❌ Microphone access denied. Check settings.';
                status.className = 'status error';
                return false;
            }
        }
        
        function initRecognition() {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            recognition.maxAlternatives = 1;
            
            recognition.onstart = function() {
                lastSpeechTime = Date.now();
                startSilenceDetection();
            };
            
            recognition.onresult = function(event) {
                const text = event.results[0][0].transcript;
                const confidence = event.results[0][0].confidence;
                
                console.log('Recognized:', text, 'Confidence:', confidence);
                
                if (confidence > 0.5) {
                    addMessage('user', text);
                    
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({
                            type: 'speech',
                            text: text,
                            confidence: confidence
                        }));
                        status.textContent = '🤖 AI is thinking...';
                        status.className = 'status speaking';
                    }
                } else {
                    console.log('Low confidence, ignoring');
                    if (isListening) {
                        setTimeout(() => recognition.start(), 500);
                    }
                }
            };
            
            recognition.onend = function() {
                if (isListening && (Date.now() - lastSpeechTime) < 30000) {
                    setTimeout(() => {
                        if (isListening) {
                            recognition.start();
                        }
                    }, 500);
                }
            };
            
            recognition.onerror = function(event) {
                console.error('Recognition error:', event.error);
                
                if (event.error === 'no-speech') {
                    status.textContent = '🎤 No speech detected. Speak louder.';
                    if (isListening) {
                        setTimeout(() => recognition.start(), 1000);
                    }
                } else if (event.error === 'not-allowed') {
                    status.textContent = '❌ Microphone blocked. Enable in settings.';
                    status.className = 'status error';
                    stopBtn.click();
                } else {
                    if (isListening) {
                        setTimeout(() => recognition.start(), 1000);
                    }
                }
            };
        }
        
        function startSilenceDetection() {
            clearTimeout(silenceTimeout);
            silenceTimeout = setTimeout(() => {
                if (isListening) {
                    console.log('Silence detected, restarting recognition');
                    recognition.stop();
                    setTimeout(() => {
                        if (isListening) recognition.start();
                    }, 500);
                }
            }, 5000);
        }
        
        function speak(text) {
            return new Promise((resolve) => {
                synthesis.cancel();
                
                // Split long text into chunks
                const chunks = text.match(/[^.!?]+[.!?]+/g) || [text];
                
                let index = 0;
                function speakNext() {
                    if (index >= chunks.length) {
                        resolve();
                        return;
                    }
                    
                    const utterance = new SpeechSynthesisUtterance(chunks[index].trim());
                    utterance.rate = 0.95;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;
                    
                    // Try to use a better voice
                    const voices = synthesis.getVoices();
                    const preferredVoice = voices.find(v => 
                        v.name.includes('Samantha') || 
                        v.name.includes('Karen') ||
                        v.name.includes('Female')
                    );
                    if (preferredVoice) {
                        utterance.voice = preferredVoice;
                    }
                    
                    utterance.onend = () => {
                        index++;
                        speakNext();
                    };
                    
                    synthesis.speak(utterance);
                }
                
                speakNext();
            });
        }
        
        function addMessage(type, text) {
            const msg = document.createElement('div');
            msg.className = 'message ' + type;
            const time = new Date().toLocaleTimeString();
            msg.innerHTML = '<strong>' + (type === 'user' ? 'You' : 'AI Agent') + ' (' + time + ')</strong>' + text;
            transcript.appendChild(msg);
            transcript.scrollTop = transcript.scrollHeight;
        }
        
        startBtn.onclick = async function() {
            // Test microphone first
            const micOk = await testMicrophone();
            if (!micOk) return;
            
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            transcript.innerHTML = '';
            
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
            
            ws.onopen = function() {
                status.textContent = '📞 Connecting...';
                status.className = 'status ready';
                ws.send(JSON.stringify({ type: 'start' }));
            };
            
            ws.onmessage = async function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'greeting') {
                    callId = data.call_id;
                    addMessage('agent', data.text);
                    status.textContent = '🔊 AI is speaking...';
                    status.className = 'status speaking';
                    
                    await speak(data.text);
                    
                    status.textContent = '🎤 Listening... (speak now)';
                    status.className = 'status listening';
                    
                    if (!isListening) {
                        initRecognition();
                        isListening = true;
                        recognition.start();
                    }
                } else if (data.type === 'response') {
                    addMessage('agent', data.text);
                    status.textContent = '🔊 AI is speaking...';
                    status.className = 'status speaking';
                    
                    await speak(data.text);
                    
                    if (data.endcall) {
                        status.textContent = '📞 Call ended';
                        status.className = 'status';
                        stopBtn.click();
                    } else {
                        status.textContent = '🎤 Listening... (speak now)';
                        status.className = 'status listening';
                        
                        if (isListening) {
                            setTimeout(() => {
                                if (isListening) recognition.start();
                            }, 500);
                        }
                    }
                }
            };
            
            ws.onerror = function() {
                status.textContent = '❌ Connection error';
                status.className = 'status error';
            };
            
            ws.onclose = function() {
                if (isListening) {
                    status.textContent = '📞 Call disconnected';
                    status.className = 'status';
                    stopBtn.click();
                }
            };
        };
        
        stopBtn.onclick = function() {
            isListening = false;
            clearTimeout(silenceTimeout);
            
            if (recognition) {
                recognition.stop();
            }
            if (ws) {
                ws.send(JSON.stringify({ type: 'end' }));
                ws.close();
            }
            synthesis.cancel();
            
            if (audioContext) {
                audioContext.close();
            }
            
            startBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
            micTest.style.display = 'none';
            status.textContent = '📞 Call ended';
            status.className = 'status';
        };
        
        // Load voices when available
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = () => {
                console.log('Voices loaded:', speechSynthesis.getVoices().length);
            };
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Create call record
    db = SessionLocal()
    call = Call(
        caller_number="Web Call",
        start_time=datetime.now(),
        status='in_progress'
    )
    db.add(call)
    db.commit()
    call_id = call.id
    db.close()
    
    conversation_history = []
    call_data = {
        'call_id': call_id,
        'history': conversation_history,
        'start_time': datetime.now()
    }
    active_calls[call_id] = call_data
    
    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str) if data_str.startswith('{') else {'type': 'text', 'text': data_str}
            
            if data['type'] == 'start':
                # Send varied greeting
                greeting = get_varied_greeting()
                conversation_history.append({"role": "assistant", "content": greeting})
                
                await websocket.send_text(json.dumps({
                    'type': 'greeting',
                    'text': greeting,
                    'call_id': call_id
                }))
                
            elif data['type'] == 'speech':
                user_text = data['text']
                confidence = data.get('confidence', 1.0)
                
                logger.info(f"[Call {call_id}] User: {user_text} (confidence: {confidence})")
                
                conversation_history.append({"role": "user", "content": user_text})
                
                # Check for goodbye
                if any(word in user_text.lower() for word in ['goodbye', 'bye', 'thank you', 'thanks', "that's all"]):
                    farewell = get_varied_farewell()
                    conversation_history.append({"role": "assistant", "content": farewell})
                    
                    await websocket.send_text(json.dumps({
                        'type': 'response',
                        'text': farewell,
                        'endcall': True
                    }))
                    
                    # Update call record
                    update_call_record(call_id, conversation_history, 'completed')
                    break
                
                # Get AI response with improved error handling
                try:
                    response = await agent.process_input(
                        user_text,
                        conversation_history,
                        call_id=call_id
                    )
                    
                    # Vary the response
                    response = vary_response(response)
                    
                    logger.info(f"[Call {call_id}] AI: {response}")
                    
                    conversation_history.append({"role": "assistant", "content": response})
                    
                    await websocket.send_text(json.dumps({
                        'type': 'response',
                        'text': response,
                        'endcall': False
                    }))
                    
                except Exception as e:
                    logger.error(f"[Call {call_id}] Error: {e}")
                    error_response = "I apologize for the confusion. Could you please repeat that?"
                    
                    await websocket.send_text(json.dumps({
                        'type': 'response',
                        'text': error_response,
                        'endcall': False
                    }))
            
            elif data['type'] == 'end':
                update_call_record(call_id, conversation_history, 'completed')
                break
                
    except WebSocketDisconnect:
        logger.info(f"[Call {call_id}] Client disconnected")
        update_call_record(call_id, conversation_history, 'disconnected')
    except Exception as e:
        logger.error(f"[Call {call_id}] Error: {e}")
        update_call_record(call_id, conversation_history, 'failed')
    finally:
        if call_id in active_calls:
            del active_calls[call_id]


def get_varied_greeting():
    """Return varied greetings"""
    import random
    greetings = [
        "Hello! Thank you for calling AI Call Center. I'm your AI assistant. How may I help you today?",
        "Good day! Welcome to AI Call Center. My name is AI Assistant. What can I do for you?",
        "Hi there! Thanks for reaching out to AI Call Center. I'm here to assist you. How can I help?",
        "Welcome! You've reached AI Call Center. I'm your virtual assistant. What brings you here today?",
        "Hello and welcome to AI Call Center! I'm ready to help. What can I assist you with?"
    ]
    return random.choice(greetings)


def get_varied_farewell():
    """Return varied farewells"""
    import random
    farewells = [
        "Thank you for calling AI Call Center. Have a wonderful day!",
        "It was my pleasure assisting you. Take care and have a great day!",
        "Thanks for reaching out. If you need anything else, feel free to call back. Goodbye!",
        "I'm glad I could help. Have an excellent day ahead!",
        "Thank you for your time. Don't hesitate to call again if you need assistance. Goodbye!"
    ]
    return random.choice(farewells)


def vary_response(response):
    """Add variety to AI responses"""
    import random
    
    # Replace common phrases with variations
    variations = {
        "I'd be happy to help": [
            "I'd be glad to assist",
            "I'll be happy to help you with that",
            "I'm here to help",
            "Let me assist you with that"
        ],
        "Can you provide": [
            "Could you please share",
            "May I have",
            "Would you mind providing",
            "Please provide"
        ],
        "I apologize": [
            "I'm sorry",
            "My apologies",
            "Please forgive me",
            "I regret"
        ],
        "Let me check": [
            "Let me look into that",
            "I'll check that for you",
            "Allow me to verify",
            "I'll look that up"
        ]
    }
    
    for phrase, alternatives in variations.items():
        if phrase in response:
            response = response.replace(phrase, random.choice(alternatives))
    
    return response


def update_call_record(call_id, conversation_history, status):
    """Update call record in database"""
    try:
        db = SessionLocal()
        call = db.query(Call).filter(Call.id == call_id).first()
        
        if call:
            call.end_time = datetime.now()
            call.duration = int((call.end_time - call.start_time).total_seconds())
            call.status = status
            
            # Create transcript
            transcript = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversation_history
            ])
            call.transcript = transcript
            
            # Detect intent from conversation
            if len(conversation_history) > 2:
                user_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
                from agent.intent_classifier import IntentClassifier
                classifier = IntentClassifier()
                call.intent = classifier.classify(" ".join(user_messages))
            
            # Determine resolution status
            if status == 'completed':
                if any(word in transcript.lower() for word in ['ticket', 'created', 'technician']):
                    call.resolution_status = 'pending'
                else:
                    call.resolution_status = 'resolved'
            else:
                call.resolution_status = 'unresolved'
            
            db.commit()
            logger.info(f"[Call {call_id}] Updated: {call.duration}s, Intent: {call.intent}, Status: {call.resolution_status}")
        
        db.close()
    except Exception as e:
        logger.error(f"Error updating call record: {e}")

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🎤 AI Call Center - Production Voice System")
    print("="*60)
    print("\n📱 iPhone (same WiFi):")
    print("   Safari → http://192.168.1.19:8004")
    print("\n💻 PC:")
    print("   Browser → http://localhost:8004")
    print("\n✨ Features:")
    print("   ✅ Varied greetings & responses")
    print("   ✅ Better error handling")
    print("   ✅ Database call recording")
    print("   ✅ Improved microphone detection")
    print("   ✅ Real-time audio level monitoring")
    print("\n💡 Tips:")
    print("   - Speak clearly after each AI response")
    print("   - Wait for 'Listening...' status")
    print("   - Say 'goodbye' to end call")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8004)

