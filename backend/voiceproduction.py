from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import asyncio
from datetime import datetime
import json
import random
sys.path.insert(0, os.path.dirname(file))

from agent.agent import AIAgent
from db.database import SessionLocal
from db.models import Call

app = FastAPI()

app.addmiddleware(
    CORSMiddleware,
    alloworigins=[""],
    allowcredentials=True,
    allowmethods=[""],
    allowheaders=[""],
)

agent = AIAgent()
activecalls = {}

html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Call Center - Enhanced</title>
    
    <style>
         { margin: 0; padding: 0; box-sizing: border-box; }
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
        .tip {
            background: #fff9c4;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 13px;
            text-align: left;
        }
        .tip strong {
            display: block;
            margin-bottom: 8px;
            color: #f57c00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 AI Call Center</h1>
        <p class="subtitle">Enhanced Interactive Voice Assistant</p>
        
        <div class="tip">
            <strong>💡 Tips for Best Experience:</strong>
            • Speak clearly after "Listening..." appears<br>
            • Wait for AI to finish speaking<br>
            • Say "goodbye" or "thank you" to end call<br>
            • Voice will speak 20% faster for efficiency
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
        
        let recognition;
        let synthesis = window.speechSynthesis;
        let ws;
        let isListening = false;
        let isSpeaking = false;
        let recognitionTimeout;
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            status.textContent = '❌ Speech not supported. Use Safari on iOS 14.5+';
            status.className = 'status error';
            startBtn.disabled = true;
        }
        
        function initRecognition() {
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            recognition.maxAlternatives = 3;
            
            let finalTranscript = '';
            let interimTranscript = '';
            
            recognition.onstart = function() {
                console.log('🎤 Listening started');
                status.textContent = '🎤 Listening... (speak now)';
                status.className = 'status listening';
            };
            
            recognition.onresult = function(event) {
                interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const result = event.results[i];
                    const transcript = result[0].transcript;
                    
                    if (result.isFinal) {
                        finalTranscript += transcript + ' ';
                        console.log('✅ Final:', finalTranscript);
                        
                        if (finalTranscript.trim().length > 0) {
                            processSpeech(finalTranscript.trim());
                            finalTranscript = '';
                        }
                    } else {
                        interimTranscript += transcript;
                        status.textContent = 🎤 Hearing: "${interimTranscript}";
                    }
                }
            };
            
            recognition.onspeechend = function() {
                console.log('🔇 Speech ended');
                setTimeout(() => {
                    if (finalTranscript.trim().length > 0) {
                        processSpeech(finalTranscript.trim());
                        finalTranscript = '';
                    }
                }, 500);
            };
            
            recognition.onend = function() {
                console.log('⏹️ Recognition ended');
                if (isListening && !isSpeaking) {
                    setTimeout(() => {
                        if (isListening) {
                            try {
                                recognition.start();
                            } catch (e) {
                                console.error('Restart error:', e);
                            }
                        }
                    }, 100);
                }
            };
            
            recognition.onerror = function(event) {
                console.error('❌ Error:', event.error);
                
                if (event.error === 'not-allowed') {
                    status.textContent = '❌ Microphone blocked';
                    status.className = 'status error';
                    alert('Enable microphone:\n1. Tap "aA" in address bar\n2. Website Settings\n3. Enable Microphone');
                    stopBtn.click();
                } else if (event.error === 'no-speech') {
                    console.log('⚠️ No speech, continuing...');
                }
            };
        }
        
        function processSpeech(text) {
            console.log('💬 Processing:', text);
            
            if (text.length < 2) return;
            
            addMessage('user', text);
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                isListening = false;
                if (recognition) recognition.stop();
                
                ws.send(JSON.stringify({
                    type: 'speech',
                    text: text,
                    confidence: 1.0
                }));
                
                status.textContent = '🤖 AI thinking...';
                status.className = 'status speaking';
            }
        }
        
        async function speak(text) {
            return new Promise((resolve) => {
                isSpeaking = true;
                synthesis.cancel();
                
                console.log('🔊 Speaking:', text);
                
                const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
                let index = 0;
                
                function speakNext() {
                    if (index >= sentences.length) {
                        isSpeaking = false;
                        resolve();
                        return;
                    }
                    
                    const utterance = new SpeechSynthesisUtterance(sentences[index].trim());
                    utterance.rate = 1.2;  // 20% FASTER
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;
                    
                    const voices = synthesis.getVoices();
                    const preferredVoice = voices.find(v => 
                        v.lang.startsWith('en') && 
                        (v.name.includes('Samantha') || 
                         v.name.includes('Karen') ||
                         v.name.includes('Female') ||
                         v.name.includes('Aria'))
                    );
                    if (preferredVoice) {
                        utterance.voice = preferredVoice;
                    }
                    
                    utterance.onend = () => {
                        index++;
                        speakNext();
                    };
                    
                    utterance.onerror = () => {
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
            const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            msg.innerHTML = '<strong>' + (type === 'user' ? 'You' : 'AI Agent') + ' ' + time + '</strong>' + text;
            transcript.appendChild(msg);
            transcript.scrollTop = transcript.scrollHeight;
        }
        
        startBtn.onclick = async function() {
            console.log('🚀 Starting call...');
            
            try {
                await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    } 
                });
                console.log('✅ Microphone granted');
            } catch (err) {
                console.error('❌ Microphone error:', err);
                status.textContent = '❌ Microphone denied';
                status.className = 'status error';
                alert('Microphone required!\n\nPlease:\n1. Tap "aA" in address bar\n2. Website Settings\n3. Enable Microphone\n4. Refresh page');
                return;
            }
            
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            transcript.innerHTML = '';
            
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
            
            ws.onopen = function() {
                console.log('🔌 Connected');
                status.textContent = '📞 Connecting...';
                status.className = 'status ready';
                ws.send(JSON.stringify({ type: 'start' }));
            };
            
            ws.onmessage = async function(event) {
                const data = JSON.parse(event.data);
                console.log('📨 Received:', data.type);
                
                if (data.type === 'greeting' || data.type === 'response') {
                    addMessage('agent', data.text);
                    status.textContent = '🔊 AI speaking...';
                    status.className = 'status speaking';
                    
                    await speak(data.text);
                    
                    if (data.end_call) {
                        status.textContent = '📞 Call ended';
                        status.className = 'status';
                        setTimeout(() => stopBtn.click(), 1000);
                    } else {
                        isListening = true;
                        
                        if (!recognition) {
                            initRecognition();
                        }
                        
                        status.textContent = '🎤 Listening...';
                        status.className = 'status listening';
                        
                        setTimeout(() => {
                            if (isListening) {
                                try {
                                    recognition.start();
                                } catch (e) {
                                    console.error('Start error:', e);
                                }
                            }
                        }, 500);
                    }
                }
            };
            
            ws.onerror = function(err) {
                console.error('❌ WebSocket error:', err);
                status.textContent = '❌ Connection error';
                status.className = 'status error';
            };
            
            ws.onclose = function() {
                console.log('🔌 WebSocket closed');
                if (isListening) {
                    stopBtn.click();
                }
            };
        };
        
        stopBtn.onclick = function() {
            console.log('⏹️ Stopping call...');
            
            isListening = false;
            isSpeaking = false;
            
            clearTimeout(recognitionTimeout);
            
            if (recognition) {
                recognition.stop();
            }
            if (ws) {
                ws.send(JSON.stringify({ type: 'end' }));
                ws.close();
            }
            synthesis.cancel();
            
            startBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            status.textContent = '📞 Call ended';
            status.className = 'status';
        };
        
        // Load voices
        if (synthesis.onvoiceschanged !== undefined) {
            synthesis.onvoiceschanged = () => {
                console.log('🎵 Voices loaded:', synthesis.getVoices().length);
            };
        }
        
        console.log('✅ Enhanced voice system loaded');
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocketendpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Create call record
    db = SessionLocal()
    call = Call(
        callernumber="Web Call",
        starttime=datetime.now(),
        status='inprogress'
    )
    db.add(call)
    db.commit()
    callid = call.id
    db.close()
    
    conversationhistory = []
    activecalls[callid] = {
        'history': conversationhistory,
        'starttime': datetime.now()
    }
    
    try:
        while True:
            datastr = await websocket.receivetext()
            data = json.loads(datastr)
            
            if data['type'] == 'start':
                # ENHANCED GREETINGS - More natural and varied
                greetings = [
                    "Hello! Thanks for calling. I'm your AI assistant. How can I help you today?",
                    "Hi there! Welcome to AI Call Center. What brings you here today?",
                    "Good day! I'm here to assist you. What can I do for you?",
                    "Hello! I'm your virtual assistant. How may I help you?",
                    "Hi! Thanks for reaching out. What can I assist you with today?"
                ]
                greeting = random.choice(greetings)
                conversationhistory.append({"role": "assistant", "content": greeting})
                
                await websocket.sendtext(json.dumps({
                    'type': 'greeting',
                    'text': greeting
                }))
                
            elif data['type'] == 'speech':
                usertext = data['text']
                conversationhistory.append({"role": "user", "content": usertext})
                
                print(f"[Call {callid}] User: {usertext}")
                
                # Check for goodbye
                goodbyephrases = ['goodbye', 'bye', 'thank you', 'thanks', "that's all", "that is all", "no thanks", "nothing else"]
                if any(phrase in usertext.lower() for phrase in goodbyephrases):
                    farewells = [
                        "Thank you for calling! Have a wonderful day!",
                        "It was my pleasure helping you. Take care!",
                        "Thanks for reaching out. Feel free to call anytime. Goodbye!",
                        "Great talking with you! Have an excellent day!",
                        "Thank you! Don't hesitate to call back if you need anything. Bye!"
                    ]
                    farewell = random.choice(farewells)
                    conversationhistory.append({"role": "assistant", "content": farewell})
                    
                    await websocket.sendtext(json.dumps({
                        'type': 'response',
                        'text': farewell,
                        'endcall': True
                    }))
                    
                    # Update database
                    updatecallrecord(callid, conversationhistory, 'completed')
                    break
                
                # Get AI response with ENHANCED agent
                try:
                    response = await agent.processinput(
                        usertext,
                        conversationhistory,
                        callid=callid
                    )
                    
                    # Make response more conversational
                    response = enhanceresponse(response, conversationhistory)
                    
                    print(f"[Call {callid}] AI: {response}")
                    
                    conversationhistory.append({"role": "assistant", "content": response})
                    
                    await websocket.sendtext(json.dumps({
                        'type': 'response',
                        'text': response,
                        'endcall': False
                    }))
                    
                except Exception as e:
                    print(f"[Call {callid}] Error: {e}")
                    errorresponses = [
                        "I apologize, could you please repeat that?",
                        "Sorry, I didn't quite catch that. Could you say it again?",
                        "Pardon me, could you rephrase that?",
                        "I'm having trouble understanding. Could you try again?"
                    ]
                    errorresponse = random.choice(errorresponses)
                    
                    await websocket.sendtext(json.dumps({
                        'type': 'response',
                        'text': errorresponse,
                        'endcall': False
                    }))
            
            elif data['type'] == 'end':
                updatecallrecord(callid, conversationhistory, 'completed')
                break
                
    except WebSocketDisconnect:
        print(f"[Call {callid}] Client disconnected")
        updatecallrecord(callid, conversationhistory, 'disconnected')
    except Exception as e:
        print(f"[Call {callid}] Error: {e}")
        updatecallrecord(callid, conversationhistory, 'failed')
    finally:
        if callid in activecalls:
            del activecalls[callid]

def enhanceresponse(response, conversationhistory):
    """
    Make AI responses more natural and conversational
    """
    # Add conversational fillers occasionally
    fillers = {
        "start": ["Well, ", "Alright, ", "Sure, ", "Okay, ", "Absolutely, "],
        "middle": [" I see.", " Got it.", " Understood.", " Makes sense."],
        "empathy": ["I understand. ", "I hear you. ", "That makes sense. "]
    }
    
    # Add empathy for problem-related queries
    problemkeywords = ['problem', 'issue', 'slow', 'not working', 'broken', 'trouble']
    if any(keyword in response.lower() for keyword in problemkeywords):
        if random.random() < 0.3:  # 30% chance
            response = random.choice(fillers['empathy']) + response
    
    # Vary common phrases
    replacements = {
        "I'd be happy to help": [
            "I'd be glad to assist",
            "I'll be happy to help you",
            "I'm here to help",
            "Let me help you with that"
        ],
        "Can you provide": [
            "Could you please share",
            "May I have",
            "Would you mind providing",
            "Could you give me"
        ],
        "I apologize": [
            "I'm sorry",
            "My apologies",
            "Sorry about that"
        ],
        "Let me check": [
            "Let me look into that",
            "I'll check that for you",
            "Allow me to verify",
            "Let me pull that up"
        ],
        "Thank you": [
            "Thanks",
            "I appreciate that",
            "Great, thank you"
        ]
    }
    
    for phrase, alternatives in replacements.items():
        if phrase in response:
            response = response.replace(phrase, random.choice(alternatives))
    
    return response

def updatecallrecord(callid, conversationhistory, status):
    """Update call record in database"""
    try:
        db = SessionLocal()
        call = db.query(Call).filter(Call.id == callid).first()
        
        if call:
            call.endtime = datetime.now()
            call.duration = int((call.endtime - call.starttime).totalseconds())
            call.status = status
            
            # Create transcript
            transcript = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversationhistory
            ])
            call.transcript = transcript
            
            # Detect intent
            if len(conversationhistory) > 2:
                usermessages = [msg['content'] for msg in conversationhistory if msg['role'] == 'user']
                from agent.intentclassifier import IntentClassifier
                classifier = IntentClassifier()
                call.intent = classifier.classify(" ".join(usermessages))
            
            # Determine resolution
            if status == 'completed':
                if any(word in transcript.lower() for word in ['ticket', 'created', 'technician']):
                    call.resolutionstatus = 'pending'
                else:
                    call.resolutionstatus = 'resolved'
            else:
                call.resolutionstatus = 'unresolved'
            
            db.commit()
            print(f"[Call {call_id}] Saved: {call.duration}s, Intent: {call.intent}")
        
        db.close()
    except Exception as e:
        print(f"Error updating call: {e}")

if name == "main":
    import uvicorn
    
    print("\n" + "="70)
    print("🎤 AI CALL CENTER - ENHANCED VOICE SYSTEM V2.0")
    print("="70)
    print("\n✨ NEW FEATURES:")
    print("   ✅ 20% faster speech (1.2x speed)")
    print("   ✅ Smarter, more conversational AI")
    print("   ✅ Varied greetings & responses")
    print("   ✅ Better error handling")
    print("   ✅ Improved speech recognition")
    print("   ✅ Database call recording")
    print("\n📱 Access Points:")
    print("   iPhone: http://192.168.1.19:8003")
    print("   PC: http://localhost:8003")
    print("\n💡 Tips:")
    print("   • Speak clearly after 'Listening...'")
    print("   • Wait for AI to finish speaking")
    print("   • Say 'goodbye' to end call")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)