# Voice System Testing Guide

## Quick Test (5 minutes)

### Step 1: Start Server
```bash
cd ai-call-center-system
start_voice.bat
```

### Step 2: Test on PC
1. Open: http://localhost:8004
2. Click "Start Call"
3. Allow microphone
4. Wait for greeting
5. Say: "I want to check my bill"
6. Say: "My customer ID is 1"
7. Listen to response

### Step 3: Test on iPhone
1. Connect to same WiFi as PC
2. Open Safari
3. Go to: http://192.168.1.19:8004
4. Click "Start Call"
5. Allow microphone (tap address bar icon)
6. Wait for greeting
7. Speak clearly

## Test Scenarios

### Scenario 1: Billing Inquiry
- **You:** "I want to check my bill"
- **AI:** "I'd be glad to assist. Could you please share your customer ID?"
- **You:** "It's 1"
- **AI:** "Your balance is $99.99. Your plan is Premium."

### Scenario 2: Technical Support
- **You:** "My internet is very slow"
- **AI:** "I'm sorry to hear that. May I have your customer ID?"
- **You:** "Customer ID 2"
- **AI:** "I've created ticket #1001. A technician will contact you."

### Scenario 3: Account Info
- **You:** "What plan am I on?"
- **AI:** "Could you please share your customer ID?"
- **You:** "3"
- **AI:** "You're on the Basic plan."

## Troubleshooting

### Microphone Not Working
- **iPhone:** Settings → Safari → Microphone → Allow
- **PC:** Browser settings → Microphone → Allow

### AI Not Responding
- Check console for errors (F12)
- Verify backend is running
- Check network connection

### Poor Voice Quality
- Speak 6-12 inches from microphone
- Reduce background noise
- Speak at normal pace

## Advanced Testing

### Test Customer IDs
- **ID 1:** John Doe, Premium, $99.99
- **ID 2:** Jane Smith, Standard, $49.99
- **ID 3:** Bob Johnson, Basic, $29.99

### Test Phrases
- "Check my bill"
- "Internet is slow"
- "What's my plan?"
- "I need help"
- "Thank you, goodbye"

## Monitoring

### View Live Calls
```bash
curl http://localhost:8000/api/calls/live
```

### View Recent Calls
```bash
curl http://localhost:8000/api/calls/recent
```

### View Dashboard
http://localhost:3000

