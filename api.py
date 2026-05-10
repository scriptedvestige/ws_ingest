#!/usr/bin/env python3

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
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

# Connect to database
db_conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)

# Create parser object
parser = process.Parser()

# --- Logging Setup --- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("weather-ingest")

# Save raw POSTS
DATA_FILE = Path("/opt/ecowitt/raw_posts.json")

# Save errors
ERROR_FILE = Path("/opt/ecowitt/error.log")

# Check API status
@app.get("/health")
def health():
    return {"status": "ok", "ts":datetime.now(timezone.utc).isoformat()}

# Endpoint for Ecowitt console to push data to
@app.post("/v1/ecowitt")
async def ingest_ecowitt(request:Request):
    """
    Receiveds Ecowitt-style HTTP POST payloads.
    """
    # Listen for the payload
    form = await request.form()
    payload = dict(form)

    # Grab timestamp from data payload
    ts_str = payload.get("dateutc")
    timestamp = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

    # Split payload into data for each table
    grouped = parser.group_payload(payload=payload)

    # Insert the proper data into its respective table
    try:
        with db_conn.cursor() as cur:
            for table, data in grouped.items():
                if not data:
                    continue
                data["time"] = timestamp
                columns = list(data.keys())
                values = list(data.values())
                placeholders = ",".join(["%s"] * len(values))
                sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                cur.execute(sql, values)
            db_conn.commit()
    except Exception as e:
        with open(ERROR_FILE, 'a') as log:
            log.write(f"{timestamp}: {str(e)}")
            return {"status": "Error", "ts":datetime.now(timezone.utc).isoformat()}

    # Log payload
    # logger.info("Ecowitt payload received: %s", payload)

    """
    with open(DATA_FILE, 'a') as file:
    #    json.dump(payload, file, default=str)
        # Processed data
        json.dump(grouped, file, default=str)
    """
        
    # If Ecowitt wants a plain-text response
    return PlainTextResponse("OK")
