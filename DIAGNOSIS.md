# Troubleshooting Report

Here are the potential issues identified in your configuration and how to fix them.

## 1. SIP Connection Issues ("Request Timeout")
**Problem:** Softphone cannot reach Asterisk.
- **Cause 1:** **Port Mismatch**. Your `docker-compose.yml` maps host port `5061` to container port `5060`.
    - **Fix:** Your softphone **MUST** use `localhost:5061` (not 5060).
- **Cause 2:** **TCP vs UDP**. Your `pjsip.conf` forces `transport-tcp`, but your softphone might be using UDP. Docker on Windows is smoother with TCP, but it crashed earlier.
    - **Fix:** We will revert everything to **UDP** on Port **5061**.

## 2. Call Failure ("Service Unavailable")
**Problem:** Call connects but immediately drops or fails.
- **Cause:** **AGI Script Connection**. The dialplan uses a hardcoded IP `172.18.0.3`.
    - **Why:** If the `backend` container restarted, it might have a new IP (e.g., `172.18.0.4`), causing the call to fail immediately.
    - **Fix:** We should use the hostname `agi://backend:4573` and ensure Docker DNS works, or update the IP.

## 3. Recommended Fix Steps

I will apply these fixes for you now:

1.  **Restore UDP Only:** Remove `transport=transport-tcp` from `pjsip.conf` to prevent crashes.
2.  **Fix AGI Address:** Update `extensions.conf` to use `agi://backend:4573` (Standard Docker DNS).
3.  **Port 5061:** Keep external port `5061` to avoid Windows conflicts.

### Your Action Required After Fixes:
Configure MicroSIP with:
- **Server:** `localhost:5061`
- **Transport:** `UDP`
- **Identity:** `6001`
