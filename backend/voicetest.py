from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agent.agent import AIAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = AIAgent()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Voice Call</title>
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
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .status {
            padding: 20px;
            margin: 20px 0;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .status.ready { background: #e8f5e9; color: #2e7d32; }
        .status.listening { background: #fff3e0; color: #e65100; }
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
        
        #startBtn {
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
        }
        #startBtn:hover { box-shadow: 0 6px 20px rgba(76,175,80,0.4); }
        
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
            min-height: 200px;
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
        }
        .instructions {
            background: #fff9c4;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 14px;
            text-align: left;
        }
        .instructions ul {
            margin: 10px 0 0 20px;
        }
        .instructions li {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 AI Voice Call</h1>
        <p class="subtitle">Speak with the AI Agent</p>
        
        <div class="instructions">
            <strong>📱 How to use:</strong>
            <ul>
                <li>Click "Start Call"</li>
                <li>Allow microphone access</li>
                <li>Wait for AI greeting</li>
                <li>Speak your question</li>
                <li>Listen to AI response</li>
            </ul>
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
        
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            status.textContent = '❌ Speech not supported in this browser';
            status.className = 'status error';
            startBtn.disabled = true;
        }
        
        function initRecognition() {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = function(event) {
                const text = event.results[0][0].transcript;
                addMessage('user', text);
                
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(text);
                    status.textContent = '🤖 AI is thinking...';
                    status.className = 'status speaking';
                }
            };
            
            recognition.onend = function() {
                if (isListening) {
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
                    status.textContent = '🎤 No speech detected, listening again...';
                    status.className = 'status listening';
                }
            };
        }
        
        function speak(text) {
            return new Promise((resolve) => {
                synthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                utterance.onend = resolve;
                synthesis.speak(utterance);
            });
        }
        
        function addMessage(type, text) {
            const msg = document.createElement('div');
            msg.className = 'message ' + type;
            msg.innerHTML = '<strong>' + (type === 'user' ? 'You' : 'AI Agent') + '</strong>' + text;
            transcript.appendChild(msg);
            transcript.scrollTop = transcript.scrollHeight;
        }
        
        startBtn.onclick = function() {
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            transcript.innerHTML = '';
            
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
            
            ws.onopen = function() {
                status.textContent = '📞 Call connected';
                status.className = 'status ready';
                ws.send('GREETING');
            };
            
            ws.onmessage = async function(event) {
                const aiResponse = event.data;
                addMessage('agent', aiResponse);
                
                status.textContent = '🔊 AI is speaking...';
                status.className = 'status speaking';
                
                await speak(aiResponse);
                
                status.textContent = '🎤 Listening... (speak now)';
                status.className = 'status listening';
                
                if (!isListening) {
                    initRecognition();
                    isListening = true;
                    recognition.start();
                }
            };
            
            ws.onerror = function() {
                status.textContent = '❌ Connection error';
                status.className = 'status error';
            };
            
            ws.onclose = function() {
                if (isListening) {
                    status.textContent = '📞 Call ended';
                    status.className = 'status';
                    stopBtn.click();
                }
            };
        };
        
        stopBtn.onclick = function() {
            isListening = false;
            if (recognition) {
                recognition.stop();
            }
            if (ws) {
                ws.close();
            }
            synthesis.cancel();
            
            startBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
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
    conversation_history = []
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "GREETING":
                greeting = agent.get_greeting()
                await websocket.send_text(greeting)
                conversation_history.append({"role": "assistant", "content": greeting})
            else:
                conversation_history.append({"role": "user", "content": data})
                
                response = await agent.process_input(
                    data,
                    conversation_history,
                    call_id=3000
                )
                
                await websocket.send_text(response)
                conversation_history.append({"role": "assistant", "content": response})
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🎤 AI Voice Call Test - FREE & EASY")
    print("="*60)
    print("\n📱 On iPhone (same WiFi):")
    print("   Open Safari → http://YOUR_IP:8003")
    print("\n💻 On PC:")
    print("   Open browser → http://localhost:8003")
    print("\n💡 Instructions:")
    print("   1. Click 'Start Call'")
    print("   2. Allow microphone")
    print("   3. Speak after AI greeting")
    print("   4. Listen to AI response")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)

