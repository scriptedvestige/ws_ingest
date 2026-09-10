#!/usr/bin/env python3

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from psycopg2 import sql
import psycopg2
import process
import logging
import json
import os

load_dotenv()

# Get database configuration
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASS")

# Start API
app = FastAPI(title="Weather Ingest", version="0.1.0")

# Create parser object
parser = process.Parser()

# --- Logging Setup --- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("weather-ingest")

# Save errors
ERROR_FILE = Path("/opt/ecowitt/error.log")

# Touch this file to dump raw payloads while adding new sensors; remove when done
DEBUG_FLAG = Path("/opt/ecowitt/DEBUG_RAW")
DEBUG_FILE = Path("/opt/ecowitt/raw_posts.json")

# --- DB connection with lazy reconnect --- #
_db_conn = None

def get_conn():
    global _db_conn
    if _db_conn is None or _db_conn.closed:
        _db_conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
    return _db_conn


def log_error(timestamp, message):
    with open(ERROR_FILE, 'a') as log:
        log.write(f"{timestamp}: {message}\n")


# Check API status
@app.get("/health")
def health():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        logger.error("Health check DB failure: %s", e)
        return {"status": "error", "detail": str(e), "ts": datetime.now(timezone.utc).isoformat()}


# Endpoint for Ecowitt console to push data to
@app.post("/v1/ecowitt")
async def ingest_ecowitt(request: Request):
    """
    Receives Ecowitt-style HTTP POST payloads.
    """
    now = datetime.now(timezone.utc)

    form = await request.form()
    payload = dict(form)

    # Optional raw payload capture, toggled by presence of DEBUG_FLAG
    if DEBUG_FLAG.exists():
        with open(DEBUG_FILE, 'a') as f:
            json.dump(payload, f, default=str)
            f.write("\n")

    # Grab timestamp from data payload
    ts_str = payload.get("dateutc")
    try:
        timestamp = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as e:
        log_error(now, f"Bad/missing dateutc={ts_str!r}: {e}")
        return {"status": "Error", "ts": now.isoformat()}

    grouped = parser.group_payload(payload=payload)

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            for table, data in grouped.items():
                if not data:
                    continue
                data["time"] = timestamp
                columns = list(data.keys())
                values = list(data.values())
                query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({placeholders})").format(
                    table=sql.Identifier(table),
                    fields=sql.SQL(',').join(map(sql.Identifier, columns)),
                    placeholders=sql.SQL(',').join(sql.Placeholder() * len(values)),
                )
                cur.execute(query, values)
        conn.commit()
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        log_error(timestamp, str(e))
        return {"status": "Error", "ts": datetime.now(timezone.utc).isoformat()}

    return PlainTextResponse("OK")
