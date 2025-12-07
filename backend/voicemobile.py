"""
Mobile-optimized voice interface
Better for iPhone Safari
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agent.agent import AIAgent
from db.database import SessionLocal
from db.models import Call
from datetime import datetime
import json
from loguru import logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = AIAgent()
active_calls = {}

html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Call - Mobile</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }
        .container {
            background: white;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            margin: 0 auto;
        }
        h1 {
            color: #667eea;
            margin-bottom: 8px;
            font-size: 24px;
            text-align: center;
        }
        .subtitle {
            color: #666;
            margin-bottom: 20px;
            font-size: 13px;
            text-align: center;
        }
        .status {
            padding: 18px;
            margin: 15px 0;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            text-align: center;
        }
        .status.ready { background: #e8f5e9; color: #2e7d32; }
        .status.listening { 
            background: #fff3e0; 
            color: #e65100;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        .status.speaking { background: #e3f2fd; color: #1565c0; }
        .status.error { background: #ffebee; color: #c62828; }
        
        button {
            width: 100%;
            padding: 18px;
            font-size: 17px;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            margin: 8px 0;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        button:active { transform: scale(0.98); }
        
        #startBtn {
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
        }
        
        #stopBtn {
            background: linear-gradient(135deg, #f44336, #e53935);
            color: white;
            display: none;
        }
        
        #transcript {
            margin-top: 20px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 12px;
            max-height: 300px;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.4;
        }
        .user {
            background: #e3f2fd;
            border-left: 3px solid #2196f3;
        }
        .agent {
            background: #f1f8e9;
            border-left: 3px solid #4caf50;
        }
        .message strong {
            display: block;
            margin-bottom: 4px;
            font-size: 11px;
            text-transform: uppercase;
            opacity: 0.7;
        }
        .tip {
            background: #fff9c4;
            padding: 12px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 13px;
            line-height: 1.5;
        }
        .tip strong {
            display: block;
            margin-bottom: 6px;
            color: #f57c00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 AI Call Center</h1>
        <p class="subtitle">Tap to start voice call</p>
        
        <div class="tip">
            <strong>💡 Quick Tips:</strong>
            • Speak after you see "Listening..."<br>
            • Wait for AI to finish speaking<br>
            • Say "goodbye" to end call
        </div>
        
        <div id="status" class="status ready">Ready</div>
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
        
        // iOS-specific setup
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            status.textContent = '❌ Use Safari on iOS 14.5+';
            status.className = 'status error';
            startBtn.disabled = true;
        }
        
        let recognitionTimeout;
        let silenceTimeout;
        
        function initRecognition() {
            recognition = new SpeechRecognition();
            
            // CRITICAL SETTINGS FOR BETTER RECOGNITION
            recognition.continuous = true;  // Keep listening
            recognition.interimResults = true;  // Get partial results
            recognition.lang = 'en-US';
            recognition.maxAlternatives = 3;  // Get multiple alternatives
            
            let finalTranscript = '';
            let interimTranscript = '';
            
            recognition.onstart = function() {
                console.log('🎤 Recognition started');
                status.textContent = '🎤 Listening... (speak now)';
                status.className = 'status listening';
                
                // Reset silence timeout
                clearTimeout(silenceTimeout);
                silenceTimeout = setTimeout(() => {
                    console.log('⏱️ Silence detected, prompting...');
                    if (isListening && !isSpeaking) {
                        status.textContent = '🎤 Still listening... (say something)';
                    }
                }, 5000);
            };
            
            recognition.onresult = function(event) {
                console.log('📝 Got result, events:', event.results.length);
                
                interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const result = event.results[i];
                    const transcript = result[0].transcript;
                    const confidence = result[0].confidence;
                    
                    console.log(`Result ${i}: "${transcript}" (${result.isFinal ? 'FINAL' : 'interim'}, confidence: ${confidence})`);
                    
                    if (result.isFinal) {
                        finalTranscript += transcript + ' ';
                        console.log('✅ Final transcript:', finalTranscript);
                        
                        // Clear timeouts
                        clearTimeout(silenceTimeout);
                        clearTimeout(recognitionTimeout);
                        
                        // Process the final transcript
                        if (finalTranscript.trim().length > 0) {
                            processSpeech(finalTranscript.trim());
                            finalTranscript = '';
                        }
                    } else {
                        interimTranscript += transcript;
                        // Show interim results to user
                        status.textContent = `🎤 Hearing: "${interimTranscript}"`;
                    }
                }
            };
            
            recognition.onspeechstart = function() {
                console.log('🗣️ Speech detected!');
                clearTimeout(silenceTimeout);
            };
            
            recognition.onspeechend = function() {
                console.log('🔇 Speech ended');
                // Give a moment for final results
                setTimeout(() => {
                    if (finalTranscript.trim().length > 0) {
                        processSpeech(finalTranscript.trim());
                        finalTranscript = '';
                    }
                }, 500);
            };
            
            recognition.onaudiostart = function() {
                console.log('🎵 Audio capture started');
            };
            
            recognition.onaudioend = function() {
                console.log('🔇 Audio capture ended');
            };
            
            recognition.onend = function() {
                console.log('⏹️ Recognition ended');
                
                if (isListening && !isSpeaking) {
                    console.log('🔄 Restarting recognition...');
                    setTimeout(() => {
                        if (isListening) {
                            try {
                                recognition.start();
                            } catch (e) {
                                console.error('Restart error:', e);
                                if (e.message.includes('already started')) {
                                    // Recognition already running, ignore
                                } else {
                                    setTimeout(() => {
                                        if (isListening) recognition.start();
                                    }, 1000);
                                }
                            }
                        }
                    }, 100);
                }
            };
            
            recognition.onerror = function(event) {
                console.error('❌ Recognition error:', event.error);
                
                if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                    status.textContent = '❌ Microphone blocked. Enable in settings.';
                    status.className = 'status error';
                    alert('Please allow microphone access:\\n\\n1. Tap the "aA" icon in address bar\\n2. Tap "Website Settings"\\n3. Enable Microphone');
                    stopBtn.click();
                } else if (event.error === 'no-speech') {
                    console.log('⚠️ No speech detected, continuing...');
                    status.textContent = '🎤 No speech heard. Speak louder?';
                    // Don't stop, just continue listening
                } else if (event.error === 'audio-capture') {
                    status.textContent = '❌ Microphone error. Check connection.';
                    status.className = 'status error';
                } else if (event.error === 'network') {
                    status.textContent = '❌ Network error. Check connection.';
                    status.className = 'status error';
                } else {
                    console.log('⚠️ Other error, continuing...');
                }
            };
        }
        
        function processSpeech(text) {
            console.log('💬 Processing speech:', text);
            
            if (text.length < 2) {
                console.log('⚠️ Text too short, ignoring');
                return;
            }
            
            addMessage('user', text);
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                // Stop listening while AI responds
                isListening = false;
                if (recognition) {
                    recognition.stop();
                }
                
                ws.send(JSON.stringify({
                    type: 'speech',
                    text: text,
                    confidence: 1.0
                }));
                
                status.textContent = '🤖 AI is thinking...';
                status.className = 'status speaking';
            }
        }
        
        async function speak(text) {
            return new Promise((resolve) => {
                isSpeaking = true;
                synthesis.cancel();
                
                console.log('🔊 Speaking:', text);
                
                // Split into sentences for better flow
                const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
                let index = 0;
                
                function speakNext() {
                    if (index >= sentences.length) {
                        isSpeaking = false;
                        console.log('✅ Finished speaking');
                        resolve();
                        return;
                    }
                    
                    const utterance = new SpeechSynthesisUtterance(sentences[index].trim());
                    utterance.rate = 0.95;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;
                    
                    // Use best available voice
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
                    
                    utterance.onerror = (e) => {
                        console.error('TTS error:', e);
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
            msg.innerHTML = '<strong>' + (type === 'user' ? 'You' : 'AI') + ' ' + time + '</strong>' + text;
            transcript.appendChild(msg);
            transcript.scrollTop = transcript.scrollHeight;
        }
        
        startBtn.onclick = async function() {
            console.log('🚀 Starting call...');
            
            // Request microphone permission explicitly
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    } 
                });
                console.log('✅ Microphone access granted');
                
                // Test if we can actually capture audio
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContext.createMediaStreamSource(stream);
                const analyser = audioContext.createAnalyser();
                source.connect(analyser);
                
                console.log('✅ Audio pipeline created');
                
            } catch (err) {
                console.error('❌ Microphone error:', err);
                status.textContent = '❌ Microphone denied';
                status.className = 'status error';
                alert('Microphone access required!\\n\\nPlease:\\n1. Tap "aA" in address bar\\n2. Tap "Website Settings"\\n3. Enable Microphone\\n4. Refresh page');
                return;
            }
            
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            transcript.innerHTML = '';
            
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
            
            ws.onopen = function() {
                console.log('🔌 WebSocket connected');
                status.textContent = '📞 Connected';
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
                    
                    if (data.endcall) {
                        status.textContent = '📞 Call ended';
                        status.className = 'status';
                        setTimeout(() => stopBtn.click(), 1000);
                    } else {
                        // Resume listening after AI finishes speaking
                        isListening = true;
                        
                        if (!recognition) {
                            initRecognition();
                        }
                        
                        status.textContent = '🎤 Listening... (your turn)';
                        status.className = 'status listening';
                        
                        setTimeout(() => {
                            if (isListening) {
                                try {
                                    recognition.start();
                                    console.log('🎤 Recognition restarted');
                                } catch (e) {
                                    console.error('Start error:', e);
                                    if (!e.message.includes('already started')) {
                                        setTimeout(() => {
                                            if (isListening) recognition.start();
                                        }, 500);
                                    }
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
            
            clearTimeout(silenceTimeout);
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
        
        // Load voices on iOS
        if (isIOS) {
            synthesis.getVoices();
            if (synthesis.onvoiceschanged !== undefined) {
                synthesis.onvoiceschanged = () => {
                    console.log('🎵 Voices loaded:', synthesis.getVoices().length);
                };
            }
        }
        
        // Debug: Log when page loads
        console.log('✅ Voice system loaded');
        console.log('📱 iOS:', isIOS);
        console.log('🎤 Speech Recognition available:', !!SpeechRecognition);
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
        caller_number="Mobile Call",
        start_time=datetime.now(),
        status='in_progress'
    )
    db.add(call)
    db.commit()
    call_id = call.id
    db.close()
    
    conversation_history = []
    active_calls[call_id] = {
        'history': conversation_history,
        'start_time': datetime.now()
    }
    
    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            if data['type'] == 'start':
                import random
                greetings = [
                    "Hello! Thank you for calling AI Call Center. How may I help you?",
                    "Hi there! Welcome to AI Call Center. What can I do for you today?",
                    "Good day! You've reached AI Call Center. How can I assist you?",
                ]
                greeting = random.choice(greetings)
                conversation_history.append({"role": "assistant", "content": greeting})
                
                await websocket.send_text(json.dumps({
                    'type': 'greeting',
                    'text': greeting
                }))
                
            elif data['type'] == 'speech':
                user_text = data['text']
                conversation_history.append({"role": "user", "content": user_text})
                
                # Check for goodbye
                if any(word in user_text.lower() for word in ['goodbye', 'bye', 'thank you', 'thanks', "that's all", "that is all"]):
                    import random
                    farewells = [
                        "Thank you for calling. Have a great day!",
                        "It was my pleasure helping you. Take care!",
                        "Thanks for reaching out. Goodbye!",
                    ]
                    farewell = random.choice(farewells)
                    conversation_history.append({"role": "assistant", "content": farewell})
                    
                    await websocket.send_text(json.dumps({
                        'type': 'response',
                        'text': farewell,
                        'endcall': True
                    }))
                    
                    # Update database
                    db = SessionLocal()
                    call = db.query(Call).filter(Call.id == call_id).first()
                    if call:
                        call.end_time = datetime.now()
                        call.duration = int((call.end_time - call.start_time).total_seconds())
                        call.status = 'completed'
                        call.transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in conversation_history])
                        db.commit()
                    db.close()
                    break
                
                # Get AI response
                try:
                    response = await agent.process_input(
                        user_text,
                        conversation_history,
                        call_id=call_id
                    )
                    
                    conversation_history.append({"role": "assistant", "content": response})
                    
                    await websocket.send_text(json.dumps({
                        'type': 'response',
                        'text': response,
                        'endcall': False
                    }))
                    
                except Exception as e:
                    logger.error(f"Error: {e}")
                    error_response = "I apologize for the confusion. Could you please repeat that?"
                    
                    await websocket.send_text(json.dumps({
                        'type': 'response',
                        'text': error_response,
                        'endcall': False
                    }))
            
            elif data['type'] == 'end':
                # Update database
                db = SessionLocal()
                call = db.query(Call).filter(Call.id == call_id).first()
                if call:
                    call.end_time = datetime.now()
                    call.duration = int((call.end_time - call.start_time).total_seconds())
                    call.status = 'completed'
                    call.transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in conversation_history])
                    db.commit()
                db.close()
                break
                
    except WebSocketDisconnect:
        logger.info(f"Client disconnected for call {call_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if call_id in active_calls:
            del active_calls[call_id]

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("📱 AI Call Center - Mobile Optimized")
    print("="*60)
    print("\niPhone: http://192.168.1.19:8004")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8004)

