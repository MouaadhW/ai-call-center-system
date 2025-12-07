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
    <title>AI Call Center Test</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 90%;
            max-width: 600px;
            height: 80vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 20px 20px 0 0;
            text-align: center;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .message {
            margin: 15px 0;
            display: flex;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .message.user {
            justify-content: flex-end;
        }
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .user .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .agent .message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .input-area {
            padding: 20px;
            background: white;
            border-radius: 0 0 20px 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        #input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #eee;
            border-radius: 25px;
            font-size: 15px;
            outline: none;
            transition: border-color 0.3s;
        }
        #input:focus {
            border-color: #667eea;
        }
        #send {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        #send:hover {
            transform: scale(1.05);
        }
        #send:active {
            transform: scale(0.95);
        }
        .typing {
            padding: 10px;
            color: #999;
            font-style: italic;
            font-size: 14px;
        }
        .status {
            padding: 10px 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            background: #f9f9f9;
        }
        .status.connected {
            color: #4caf50;
        }
        .status.disconnected {
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Call Center</h1>
            <p>Test the AI Agent - Type your message below</p>
        </div>
        <div class="status" id="status">Connecting...</div>
        <div id="chat"></div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Type your message..." disabled>
            <button id="send" disabled>Send</button>
        </div>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');
        const send = document.getElementById('send');
        const status = document.getElementById('status');
        let ws;
        let isTyping = false;

        function connect() {
            ws = new WebSocket('ws://localhost:8001/ws');
            
            ws.onopen = function() {
                status.textContent = '✓ Connected';
                status.className = 'status connected';
                input.disabled = false;
                send.disabled = false;
                ws.send('__GREETING__');
            };
            
            ws.onclose = function() {
                status.textContent = '✗ Disconnected';
                status.className = 'status disconnected';
                input.disabled = true;
                send.disabled = true;
                setTimeout(connect, 3000);
            };
            
            ws.onerror = function() {
                status.textContent = '✗ Connection Error';
                status.className = 'status disconnected';
            };
            
            ws.onmessage = function(event) {
                if (isTyping) {
                    const typing = document.querySelector('.typing');
                    if (typing) typing.remove();
                    isTyping = false;
                }
                const msgDiv = document.createElement('div');
                msgDiv.className = 'message agent';
                msgDiv.innerHTML = '<div class="message-content">' + event.data + '</div>';
                chat.appendChild(msgDiv);
                chat.scrollTop = chat.scrollHeight;
            };
        }

        function sendMessage() {
            const text = input.value.trim();
            if (text && ws.readyState === WebSocket.OPEN) {
                const msgDiv = document.createElement('div');
                msgDiv.className = 'message user';
                msgDiv.innerHTML = '<div class="message-content">' + text + '</div>';
                chat.appendChild(msgDiv);
                
                const typingDiv = document.createElement('div');
                typingDiv.className = 'typing';
                typingDiv.textContent = 'AI is typing...';
                chat.appendChild(typingDiv);
                isTyping = true;
                
                ws.send(text);
                input.value = '';
                chat.scrollTop = chat.scrollHeight;
            }
        }

        send.onclick = sendMessage;
        input.onkeypress = function(e) {
            if (e.key === 'Enter') sendMessage();
        };

        connect();
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
            
            if data == "__GREETING__":
                greeting = agent.get_greeting()
                await websocket.send_text(greeting)
                conversation_history.append({"role": "assistant", "content": greeting})
            else:
                conversation_history.append({"role": "user", "content": data})
                response = await agent.process_input(
                    data,
                    conversation_history,
                    call_id=1000
                )
                await websocket.send_text(response)
                conversation_history.append({"role": "assistant", "content": response})
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 AI Call Center Web Test Interface")
    print("="*60)
    print("\n📱 Open in your browser: http://localhost:8001")
    print("\n💡 Test conversations:")
    print("   - 'I want to check my bill'")
    print("   - 'My internet is slow'")
    print("   - 'What's my account status?'")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)

