"""Business logic to calculate OEE from InfluxDB measurements."""

from datetime import datetime
from typing import Dict, Optional

from . import acquisition, config


def _query_sum(section: str, field: str, start: str, end: str) -> float:
    """Return the sum of ``field`` for ``section`` between ``start`` and ``end``."""
    query_api = acquisition.get_client().query_api()
    query = (
        f'from(bucket:"{config.INFLUXDB_BUCKET}") '
        f'|> range(start: {start}, stop: {end}) '
        f'|> filter(fn: (r) => r["_measurement"] == "{section}") '
        f'|> filter(fn: (r) => r["_field"] == "{field}") '
        '|> sum()'
    )
    try:
        tables = query_api.query(query)
    except Exception:
        return 0.0
    for table in tables:
        for record in table.records:
            return float(record.get_value())
    return 0.0


def _query_avg(section: str, field: str, start: str, end: str) -> float:
    """Return the average of ``field`` for ``section`` between ``start`` and ``end``."""
    query_api = acquisition.get_client().query_api()
    query = (
        f'from(bucket:"{config.INFLUXDB_BUCKET}") '
        f'|> range(start: {start}, stop: {end}) '
        f'|> filter(fn: (r) => r["_measurement"] == "{section}") '
        f'|> filter(fn: (r) => r["_field"] == "{field}") '
        '|> mean()'
    )
    try:
        tables = query_api.query(query)
    except Exception:
        return 0.0
    for table in tables:
        for record in table.records:
            return float(record.get_value())
    return 0.0


def calculate_oee(section: str, start: str, end: str) -> Dict[str, float]:
    """Return Availability, Performance, Quality and total OEE.

    Example::

        calculate_oee("blistera", "-1h", "now()")
    """
    if section == "blistera":
        formed_field = "blister_formados"
        rejected_field = "blister_rechazados"
    else:
        formed_field = "estuches_formados"
        rejected_field = "estuches_rechazados"

    formed = _query_sum(section, formed_field, start, end)
    rejected = _query_sum(section, rejected_field, start, end)
    quality = (formed - rejected) / formed * 100 if formed else 0

    if section == "blistera":
        speed_field = "velocidad_formacion"
    else:
        speed_field = "velocidad_estuchado"

    avg_speed = _query_avg(section, speed_field, start, end)
    performance = avg_speed
    availability = 100.0
    oee = quality * performance * availability / 10000
    return {
        "availability": availability,
        "performance": performance,
        "quality": quality,
        "oee": oee,
    }
