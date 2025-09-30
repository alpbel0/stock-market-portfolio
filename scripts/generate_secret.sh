#!/usr/bin/env bash
set -euo pipefail

TARGET_FILE="${1:-.env}"
KEY_NAME="${2:-SECRET_KEY}"

# Generate a strong random key (base64, 32 bytes). Fallback to Python if openssl is not available.
if command -v openssl >/dev/null 2>&1; then
  SECRET=$(openssl rand -base64 32 | tr -d '\n')
else
  SECRET=$(python3 - <<'PY'
import os, base64
print(base64.b64encode(os.urandom(32)).decode('utf-8'))
PY
)
fi

# Ensure target file exists
if [ ! -f "$TARGET_FILE" ]; then
  touch "$TARGET_FILE"
fi

# Insert or replace the SECRET_KEY without printing it to stdout
if grep -qE "^${KEY_NAME}=.*" "$TARGET_FILE"; then
  sed -i "s/^${KEY_NAME}=.*/${KEY_NAME}=${SECRET}/" "$TARGET_FILE"
else
  printf "\n${KEY_NAME}=${SECRET}\n" >> "$TARGET_FILE"
fi

# Restrict permissions on the env file
chmod 600 "$TARGET_FILE"

echo "A new ${KEY_NAME} has been generated and stored in ${TARGET_FILE}."
