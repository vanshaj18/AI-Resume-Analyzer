#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env if present (safe parsing; no variable expansion)
load_env() {
  local env_file="$1"
  [ -f "$env_file" ] || return 0
  while IFS= read -r line || [ -n "$line" ]; do
    # Skip comments and empty lines
    case "$line" in
      ""|\#*) continue ;;
    esac
    # Strip leading "export "
    line="${line#export }"
    # Split on first '='
    local key="${line%%=*}"
    local val="${line#*=}"
    # Trim whitespace around key
    key="$(echo "$key" | sed 's/[[:space:]]//g')"
    # Remove surrounding quotes from value if present
    if [[ "$val" == \"*\" && "$val" == *\" ]]; then
      val="${val:1:${#val}-2}"
    elif [[ "$val" == \'*\' && "$val" == *\' ]]; then
      val="${val:1:${#val}-2}"
    fi
    # Export without expansion
    printf -v "$key" '%s' "$val"
    export "$key"
  done < "$env_file"
}

load_env ".env"

PYTHON_BIN="${PYTHON_BIN:-python3.12}"

UI_IP="${UI_IP:-127.0.0.1}"
UI_PORT="${UI_PORT:-8000}"
BACKEND_IP="${BACKEND_IP:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8001}"
CELERY_CONCURRENCY="${CELERY_CONCURRENCY:-4}"

VENV_DIR="${VENV_DIR:-.venv}"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating venv at ${VENV_DIR}..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# Activate venv
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if command -v redis-server >/dev/null 2>&1; then
  if ! pgrep -x redis-server >/dev/null 2>&1; then
    echo "Starting Redis..."
    redis-server --daemonize yes
  else
    echo "Redis already running."
  fi
else
  echo "redis-server not found. Install Redis to run Celery locally."
fi

echo "ENVIRONMENT=$ENVIRONMENT"
echo "REDIS_URL=$REDIS_URL"

echo "Starting Celery worker..."
python -m celery -A backend.celery_app worker -l info -Q extraction --concurrency 1 &
python -m celery -A backend.celery_app worker -l info -Q analysis --concurrency "$CELERY_CONCURRENCY" &
CELERY_PID=$!

echo "Starting API server on ${BACKEND_IP}:${BACKEND_PORT}..."
python -m uvicorn analysis.app:app --host "$BACKEND_IP" --port "$BACKEND_PORT" &
API_PID=$!

cleanup() {
  echo "Shutting down background processes..."
  kill "$CELERY_PID" "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "Starting UI server on ${UI_IP}:${UI_PORT}..."
python manage.py runserver "${UI_IP}:${UI_PORT}"
