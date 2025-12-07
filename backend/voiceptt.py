"""
Push-to-Talk version - More reliable for iPhone
User holds button to speak
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
    <title>AI Call - Push to Talk</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
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
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 25px;
            font-size: 14px;
        }
        .status {
            padding: 20px;
            margin: 20px 0;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
        }
        .status.ready { background: #e8f5e9; color: #2e7d32; }
        .status.listening { 
            background: #fff3e0; 
            color: #e65100;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        .status.speaking { background: #e3f2fd; color: #1565c0; }
        .status.error { background: #ffebee; color: #c62828; }
        
        #talkBtn {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            border: none;
            font-size: 24px;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, #4caf50, #45a049);
            box-shadow: 0 10px 30px rgba(76,175,80,0.4);
            cursor: pointer;
            margin: 30px auto;
            display: block;
            transition: all 0.2s;
            touch-action: manipulation;
        }
        #talkBtn:active {
            transform: scale(0.95);
            box-shadow: 0 5px 15px rgba(76,175,80,0.6);
        }
        #talkBtn.recording {
            background: linear-gradient(135deg, #f44336, #e53935);
            animation: recordingPulse 1s infinite;
        }
        @keyframes recordingPulse {
            0%, 100% { box-shadow: 0 10px 30px rgba(244,67,54,0.4); }
            50% { box-shadow: 0 10px 40px rgba(244,67,54,0.8); }
        }
        
        #startBtn, #stopBtn {
            width: 100%;
            padding: 18px;
            font-size: 17px;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            margin: 8px 0;
            transition: all 0.2s;
        }
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
            text-align: left;
            -webkit-overflow-scrolling: touch;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 AI Call Center</h1>
        <p class="subtitle">Push to Talk - Hold button to speak</p>
        
        <div class="instructions">
            <strong>💡 How to use:</strong>
            <ol style="margin-left: 20px;">
                <li>Click "Start Call"</li>
                <li>Wait for AI greeting</li>
                <li>Hold the big button to speak</li>
                <li>Release when done</li>
                <li>Listen to AI response</li>
            </ol>
        </div>
        
        <div id="status" class="status ready">Ready</div>
        <button id="startBtn">📞 Start Call</button>
        <button id="stopBtn">📞 End Call</button>
        <button id="talkBtn" style="display:none;">🎤 Hold to Talk</button>
        <div id="transcript"></div>
    </div>
    
    <script>
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const talkBtn = document.getElementById('talkBtn');
        const status = document.getElementById('status');
        const transcript = document.getElementById('transcript');
        
        let recognition;
        let synthesis = window.speechSynthesis;
        let ws;
        let isCallActive = false;
        let isRecording = false;
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            status.textContent = '❌ Use Safari on iOS 14.5+';
            status.className = 'status error';
            startBtn.disabled = true;
        }
        
        function initRecognition() {
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onresult = function(event) {
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript + ' ';
                    }
                }
                
                if (finalTranscript.trim()) {
                    console.log('Heard:', finalTranscript);
                }
            };
            
            recognition.onend = function() {
                if (isRecording) {
                    recognition.start();
                }
            };
        }
        
        async function speak(text) {
            return new Promise((resolve) => {
                synthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.95;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                const voices = synthesis.getVoices();
                const preferredVoice = voices.find(v => 
                    v.lang.startsWith('en') && 
                    (v.name.includes('Samantha') || v.name.includes('Female'))
                );
                if (preferredVoice) {
                    utterance.voice = preferredVoice;
                }
                
                utterance.onend = resolve;
                synthesis.speak(utterance);
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
        
        // Push to talk handlers
        talkBtn.addEventListener('touchstart', startRecording, {passive: true});
        talkBtn.addEventListener('touchend', stopRecording, {passive: true});
        talkBtn.addEventListener('mousedown', startRecording);
        talkBtn.addEventListener('mouseup', stopRecording);
        talkBtn.addEventListener('mouseleave', stopRecording);
        
        let recordingTranscript = '';
        
        function startRecording(e) {
            e.preventDefault();
            if (!isCallActive || isRecording) return;
            
            isRecording = true;
            recordingTranscript = '';
            talkBtn.classList.add('recording');
            talkBtn.textContent = '🔴 Recording...';
            status.textContent = '🎤 Recording... (release when done)';
            status.className = 'status listening';
            
            if (!recognition) {
                initRecognition();
            }
            
            recognition.onresult = function(event) {
                let interim = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        recordingTranscript += event.results[i][0].transcript + ' ';
                    } else {
                        interim += event.results[i][0].transcript;
                    }
                }
                if (interim) {
                    status.textContent = `🎤 Hearing: "${interim}"`;
                }
            };
            
            try {
                recognition.start();
                console.log('Recording started');
            } catch (e) {
                console.error('Start error:', e);
            }
        }
        
        function stopRecording(e) {
            e.preventDefault();
            if (!isRecording) return;
            
            isRecording = false;
            talkBtn.classList.remove('recording');
            talkBtn.textContent = '🎤 Hold to Talk';
            
            if (recognition) {
                recognition.stop();
            }
            
            setTimeout(() => {
                if (recordingTranscript.trim().length > 2) {
                    processSpeech(recordingTranscript.trim());
                } else {
                    status.textContent = '🎤 No speech detected. Try again.';
                    status.className = 'status';
                }
                recordingTranscript = '';
            }, 500);
        }
        
        function processSpeech(text) {
            addMessage('user', text);
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'speech',
                    text: text,
                    confidence: 1.0
                }));
                
                status.textContent = '🤖 AI thinking...';
                status.className = 'status speaking';
            }
        }
        
        startBtn.onclick = async function() {
            try {
                await navigator.mediaDevices.getUserMedia({ audio: true });
            } catch (err) {
                status.textContent = '❌ Microphone denied';
                status.className = 'status error';
                alert('Please allow microphone access');
                return;
            }
            
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            talkBtn.style.display = 'block';
            transcript.innerHTML = '';
            
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
            
            ws.onopen = function() {
                isCallActive = true;
                status.textContent = '📞 Connected';
                status.className = 'status ready';
                ws.send(JSON.stringify({ type: 'start' }));
            };
            
            ws.onmessage = async function(event) {
                const data = JSON.parse(event.data);
                
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
                        status.textContent = '🎤 Hold button to speak';
                        status.className = 'status ready';
                    }
                }
            };
            
            ws.onerror = function() {
                status.textContent = '❌ Connection error';
                status.className = 'status error';
            };
            
            ws.onclose = function() {
                stopBtn.click();
            };
        };
        
        stopBtn.onclick = function() {
            isCallActive = false;
            isRecording = false;
            
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
            talkBtn.style.display = 'none';
            status.textContent = '📞 Call ended';
            status.className = 'status';
        };
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
    
    db = SessionLocal()
    call = Call(
        caller_number="PTT Call",
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
                
                if any(word in user_text.lower() for word in ['goodbye', 'bye', 'thank you', 'thanks', "that's all"]):
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
                    
                    db = SessionLocal()
                    call = db.query(Call).filter(Call.id == call_id).first()
                    if call:
                        call.end_time = datetime.now()
                        call.duration = int((call.end_time - call.start_time).total_seconds())
                        call.status = 'completed'
                        call.transcript = "\\n".join([f"{m['role'].upper()}: {m['content']}" for m in conversation_history])
                        db.commit()
                    db.close()
                    break
                
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
                db = SessionLocal()
                call = db.query(Call).filter(Call.id == call_id).first()
                if call:
                    call.end_time = datetime.now()
                    call.duration = int((call.end_time - call.start_time).total_seconds())
                    call.status = 'completed'
                    call.transcript = "\\n".join([f"{m['role'].upper()}: {m['content']}" for m in conversation_history])
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
    
    print("\\n" + "="*60)
    print("🎤 AI Call Center - Push to Talk")
    print("="*60)
    print("\\n📱 iPhone: http://192.168.1.19:8005")
    print("💻 PC: http://localhost:8005")
    print("="*60 + "\\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)

