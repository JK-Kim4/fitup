#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
GUNICORN_PID="$PROJECT_DIR/gunicorn.pid"

echo "[1/2] Gunicorn 종료"
if [ -f "$GUNICORN_PID" ]; then
    PID=$(cat "$GUNICORN_PID")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "  종료됨 (PID: $PID)"
    else
        echo "  프로세스가 이미 없음 (PID: $PID)"
    fi
    rm -f "$GUNICORN_PID"
else
    echo "  gunicorn.pid 파일 없음 (이미 종료 상태)"
fi

echo "[2/2] PostgreSQL 컨테이너 종료"
docker compose -f "$PROJECT_DIR/docker-compose.yml" down

echo ""
echo "서버 종료 완료"
