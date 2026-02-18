#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$PROJECT_DIR/venv/bin"
GUNICORN_PID="$PROJECT_DIR/gunicorn.pid"
GUNICORN_LOG="$PROJECT_DIR/gunicorn.log"
BIND="0.0.0.0:8000"
WORKERS=3

# ── [1/5] .env 확인 ──────────────────────────────────────────
echo "[1/5] 환경변수 로드"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "ERROR: .env 파일이 없습니다."
    echo "  cp .env.example .env 후 값을 채워주세요."
    exit 1
fi
set -a
source "$PROJECT_DIR/.env"
set +a

# ── [2/5] PostgreSQL 컨테이너 확인 ──────────────────────────
echo "[2/5] PostgreSQL 컨테이너 확인"
DB_STATUS=$(docker compose -f "$PROJECT_DIR/docker-compose.yml" ps --format json db 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0].get('Health',''))" 2>/dev/null || echo "")

if [ "$DB_STATUS" != "healthy" ]; then
    echo "  PostgreSQL 시작 중..."
    docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d

    echo -n "  DB 준비 대기"
    for i in $(seq 1 30); do
        sleep 2
        READY=$(docker compose -f "$PROJECT_DIR/docker-compose.yml" ps --format json db 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0].get('Health',''))" 2>/dev/null || echo "")
        if [ "$READY" = "healthy" ]; then
            echo " 완료"
            break
        fi
        echo -n "."
        if [ "$i" -eq 30 ]; then
            echo ""
            echo "ERROR: DB가 30회 대기 후에도 healthy 상태가 아닙니다."
            echo "  docker compose logs db 로 확인하세요."
            exit 1
        fi
    done
else
    echo "  PostgreSQL 이미 실행 중"
fi

# ── [3/5] 패키지 설치 ────────────────────────────────────────
echo "[3/5] 패키지 설치"
"$VENV/pip" install -r "$PROJECT_DIR/requirements.txt" -q

# ── [4/5] 마이그레이션 & 정적 파일 ──────────────────────────
echo "[4/5] 마이그레이션 및 정적 파일 수집"
"$VENV/python" "$PROJECT_DIR/manage.py" migrate --noinput
"$VENV/python" "$PROJECT_DIR/manage.py" collectstatic --noinput --clear -v 0

# ── [5/5] Gunicorn 재시작 ────────────────────────────────────
echo "[5/5] Gunicorn 시작"
if [ -f "$GUNICORN_PID" ]; then
    PID=$(cat "$GUNICORN_PID")
    if kill -0 "$PID" 2>/dev/null; then
        echo "  기존 프로세스 종료 (PID: $PID)"
        kill "$PID"
        sleep 2
    fi
    rm -f "$GUNICORN_PID"
fi

"$VENV/gunicorn" config.wsgi:application \
    --bind "$BIND" \
    --workers "$WORKERS" \
    --pid "$GUNICORN_PID" \
    --log-file "$GUNICORN_LOG" \
    --access-logfile "$GUNICORN_LOG" \
    --daemon

echo ""
echo "배포 완료"
echo "  서버   : http://localhost:8000"
echo "  로그   : $GUNICORN_LOG"
echo "  PID    : $(cat "$GUNICORN_PID")"
