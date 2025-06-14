"""Local buffer for measurements when InfluxDB is unreachable."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import List, Dict

from influxdb_client import InfluxDBClient, Point, WriteApi, SYNCHRONOUS

from . import config

BUFFER_FILE = Path("data/buffer/buffer.json")
RESEND_INTERVAL = 30  # seconds


def save_to_buffer(data: Dict) -> None:
    """Append measurement ``data`` to the JSON buffer."""
    BUFFER_FILE.parent.mkdir(parents=True, exist_ok=True)
    if BUFFER_FILE.exists():
        buf = json.loads(BUFFER_FILE.read_text())
    else:
        buf = []
    buf.append(data)
    BUFFER_FILE.write_text(json.dumps(buf, indent=2))


def _load_buffer() -> List[Dict]:
    if BUFFER_FILE.exists():
        return json.loads(BUFFER_FILE.read_text())
    return []


def _save_buffer(entries: List[Dict]) -> None:
    BUFFER_FILE.parent.mkdir(parents=True, exist_ok=True)
    BUFFER_FILE.write_text(json.dumps(entries, indent=2))


def _get_client() -> InfluxDBClient:
    return InfluxDBClient(
        url=config.INFLUXDB_URL,
        token=config.INFLUXDB_TOKEN,
        org=config.INFLUXDB_ORG,
    )


async def retry_buffer_upload() -> None:
    """Periodically attempt to resend buffered data to InfluxDB."""
    while True:
        await asyncio.sleep(RESEND_INTERVAL)
        entries = _load_buffer()
        if not entries:
            continue
        try:
            client = _get_client()
            write_api = client.write_api(write_options=SYNCHRONOUS)
        except Exception:
            continue
        remaining = []
        for row in entries:
            try:
                point = Point(row["measurement"])
                ts = row.get("timestamp")
                if ts:
                    point.time(ts)
                for k, v in row.get("fields", {}).items():
                    point.field(k, v)
                write_api.write(bucket=config.INFLUXDB_BUCKET, record=point)
            except Exception:
                remaining.append(row)
        _save_buffer(remaining)

