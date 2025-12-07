# Final Setup Instructions

The system is currently building. Once the build completes (this may take 10-15 minutes due to AI model dependencies), follow these steps:

## 1. Initialize the Database

Run this command to create the database tables and add sample data:

```bash
docker exec -it backend python -m db.init_db
```

## 2. Verify System Status

Check if all containers are running:

```bash
docker-compose ps
```

You should see 3 services: `asterisk`, `backend`, and `dashboard` with status `Up`.

## 3. Run System Tests

Run the automated test suite to verify connections:

```bash
python scripts/test_call.py
```

## 4. Access the System

- **Dashboard:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Asterisk SIP:** localhost:5060

## 5. Make a Test Call

1. Install a SIP softphone (e.g., Zoiper, Linphone, MicroSIP).
2. Configure a new account:
   - **Domain/Server:** localhost:5060
   - **Username:** 6001
   - **Password:** 6001
   - **Transport:** UDP
3. Dial extension **100**.
4. Speak to the AI agent!

## Troubleshooting

If the build fails or services don't start:

1. **Check logs:**
   ```bash
   docker-compose logs -f
   ```

2. **Rebuild specific service:**
   ```bash
   docker-compose up -d --build backend
   ```

3. **Restart all:**
   ```bash
   docker-compose restart
   ```

Enjoy your AI Call Center! 🚀
