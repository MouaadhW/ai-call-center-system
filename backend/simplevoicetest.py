from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>✅ Server is Working!</h1>
        <p>If you see this, the server is running correctly.</p>
        <button onclick="testSpeech()" style="padding: 15px 30px; font-size: 18px; cursor: pointer; background: #4CAF50; color: white; border: none; border-radius: 5px;">Test Speech</button>
        <div id="result" style="margin-top: 20px;"></div>
        
        <script>
        function testSpeech() {
            const msg = new SpeechSynthesisUtterance("Hello! The voice system is working!");
            window.speechSynthesis.speak(msg);
            document.getElementById('result').innerHTML = '<p style="color: green; font-size: 18px;">✅ Speech working!</p>';
        }
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Simple Test Server")
    print("="*60)
    print("\nPC: http://localhost:8005")
    print("iPhone: http://192.168.1.19:8005")
    print("\n" + "="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8005)

