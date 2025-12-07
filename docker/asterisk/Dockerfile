FROM debian:bullseye-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    asterisk \
    asterisk-core-sounds-en \
    asterisk-core-sounds-en-gsm \
    asterisk-moh-opsound-gsm \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /var/log/asterisk \
    && mkdir -p /var/spool/asterisk \
    && chown -R asterisk:asterisk /var/log/asterisk /var/spool/asterisk

# Copy logger configuration
COPY logger.conf /etc/asterisk/logger.conf

# Expose ports
EXPOSE 5060/udp 5060/tcp 10000-10099/udp 4573

# Run as asterisk user
# USER asterisk

# Start Asterisk with verbose logging
CMD ["asterisk", "-f", "-vvvvv"]
