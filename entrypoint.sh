#!/bin/bash
set -e

# Default values if not provided
PUID=${PUID:-1000}
PGID=${PGID:-1000}

echo "Using PUID=${PUID}, PGID=${PGID}"

# Create group if needed
if ! getent group submate >/dev/null; then
    groupadd -g "$PGID" submate
fi

# Create user if needed
if ! id -u submate >/dev/null 2>&1; then
    useradd -u "$PUID" -g "$PGID" -m submate
fi

# Fix permissions on app directory
chown -R "$PUID":"$PGID" /app

# Drop privileges and run the app
exec gosu submate "$@"
