#!/bin/bash
# Start Asterisk with error handling for Stasis

# Create necessary directories
mkdir -p /var/run/asterisk
chown -R asterisk:asterisk /var/run/asterisk /var/log/asterisk /var/spool/asterisk

# Try to start Asterisk, ignore Stasis errors
asterisk -f -vvvvv 2>&1 | grep -v "Stasis initialization failed" || true

# If Asterisk exits, try starting it again without Stasis
if ! pgrep -x asterisk > /dev/null; then
    echo "Asterisk exited, attempting restart without Stasis modules..."
    # Disable Stasis in modules.conf if not already done
    sed -i 's/^load => res_stasis/#load => res_stasis/g' /etc/asterisk/modules.conf
    asterisk -f -vvvvv
fi

