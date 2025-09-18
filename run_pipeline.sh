#!/usr/bin/env bash
set -euo pipefail

# === Configuration ===
PROJECT_DIR="/mnt/d/university/sem-7/data engineering/project2/retail-analytics-pipeline_2"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP="$(date +'%Y-%m-%d_%H-%M-%S')"
RUN_LOG="$LOG_DIR/run_$TIMESTAMP.log"

# Ensure logs directory exists
mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

echo "[$(date)] 🚀 Starting pipeline run..." | tee -a "$RUN_LOG"

# 1) Ensure postgres container is up
if ! docker ps --format '{{.Names}}' | grep -q '^retail_pg$'; then
  echo "[$(date)] 🐘 Starting postgres container..." | tee -a "$RUN_LOG"
  docker compose up -d postgres >> "$RUN_LOG" 2>&1
else
  echo "[$(date)] 🐘 Postgres container already running." | tee -a "$RUN_LOG"
fi

# 2) Wait for postgres to be ready
echo "[$(date)] ⏳ Waiting for Postgres to be ready..." | tee -a "$RUN_LOG"
until docker exec retail_pg pg_isready -U retail_user -d retail_db -h localhost >/dev/null 2>&1; do
  sleep 2
done
echo "[$(date)] ✅ Postgres is ready." | tee -a "$RUN_LOG"

# 3) Activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
  source "$VENV_DIR/bin/activate"
  echo "[$(date)] 📦 Virtual environment activated." | tee -a "$RUN_LOG"
else
  echo "[$(date)] ❌ Virtual environment not found at $VENV_DIR" | tee -a "$RUN_LOG"
  exit 1
fi

# 4) Run the pipeline
echo "[$(date)] ▶️ Running pipeline.py..." | tee -a "$RUN_LOG"
if python pipeline.py >> "$RUN_LOG" 2>&1; then
  echo "[$(date)] 🎉 Pipeline finished successfully." | tee -a "$RUN_LOG"
else
  RC=$?
  echo "[$(date)] ❌ Pipeline failed with exit code $RC." | tee -a "$RUN_LOG"
  exit $RC
fi
