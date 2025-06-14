"""Data acquisition simulation and store & forward buffer."""
from __future__ import annotations

import asyncio
import random
from datetime import datetime
from typing import Dict

from influxdb_client import InfluxDBClient, Point, WriteOptions
from . import config, store_forward

# Connection parameters for InfluxDB
INFLUXDB_URL = config.INFLUXDB_URL
INFLUXDB_TOKEN = config.INFLUXDB_TOKEN
INFLUXDB_ORG = config.INFLUXDB_ORG
INFLUXDB_BUCKET = config.INFLUXDB_BUCKET
ACQUISITION_INTERVAL = config.ACQUISITION_INTERVAL_SECONDS

_client: InfluxDBClient | None = None


def influx_available() -> bool:
    """Return True if InfluxDB is reachable."""
    try:
        return get_client().ping() is True
    except Exception:
        return False


def get_client() -> InfluxDBClient:
    global _client
    if _client is None:
        _client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    return _client


# Data simulation helpers -----------------------------------------------------

def generate_blistera_data() -> Dict[str, int]:
    """Return a random measurement sample for *Blistera*."""
    return {
        "velocidad_formacion": random.randint(50, 100),
        "blister_formados": random.randint(1000, 2000),
        "blister_rechazados": random.randint(0, 50),
    }


def generate_estuchadora_data() -> Dict[str, int]:
    """Return a random measurement sample for *Estuchadora*."""
    return {
        "velocidad_estuchado": random.randint(40, 90),
        "estuches_formados": random.randint(900, 1800),
        "estuches_rechazados": random.randint(0, 40),
    }


# Buffer management is delegated to :mod:`store_forward`.


# Acquisition loops ----------------------------------------------------------

async def acquisition_loop() -> None:
    """Background task that simulates tag acquisition."""
    write_api = get_client().write_api(write_options=WriteOptions(batch_size=1))
    while True:
        await asyncio.sleep(ACQUISITION_INTERVAL)
        for section, generator in {
            "blistera": generate_blistera_data,
            "estuchadora": generate_estuchadora_data,
        }.items():
            data = generator()
            point = Point(section)
            for k, v in data.items():
                point.field(k, v)
            point.time(datetime.utcnow())
            try:
                write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            except Exception:
                store_forward.save_to_buffer(
                    {
                        "measurement": section,
                        "timestamp": datetime.utcnow().isoformat(),
                        "fields": data,
                    }
                )


async def start_acquisition_tasks() -> None:
    """Launch acquisition and resend tasks when the application starts.

    Should be called in the application startup event::

        @app.on_event("startup")
        async def startup():
            await acquisition.start_acquisition_tasks()
    """
    asyncio.create_task(acquisition_loop())
    asyncio.create_task(store_forward.retry_buffer_upload())

