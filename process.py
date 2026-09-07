#!/usr/bin/env python3

from datetime import datetime, timezone
import logging

logger = logging.getLogger("weather-ingest")


class Parser:
    """
    Split the data up into smaller chunks to be saved to the appropriate table.
    """
    def __init__(self):
        self.SENSOR_KEYS = {
            "ws_observations": [
                "baromabsin",
                "tempf",
                "humidity",
                "winddir",
                "windspeedmph",
                "windgustmph",
                "maxdailygust",
                "solarradiation",
                "uv",
                "vpd",
                "rainratein",
                "eventrainin"
            ],
            "console_obs": [
                "tempinf",
                "humidityin",
            ],
            "office_obs": [
                "temp2f",
                "humidity2"
            ],
            "rain_totals": [
                "hourlyrainin",
                "dailyrainin",
                "weeklyrainin",
                "monthlyrainin",
                "yearlyrainin"
            ],
            "lightning_events": [
                "lightning_num",
                "lightning_time",
                "lightning"
            ]
        }

    def group_payload(self, payload: dict) -> dict:
        grouped = {
            sensor: {
                k: self.conversions(payload[k], field=k)
                for k in keys if k in payload
            }
            for sensor, keys in self.SENSOR_KEYS.items()
        }
        # Rename lightning field to lightning_mi
        if 'lightning_events' in grouped and 'lightning' in grouped['lightning_events']:
            grouped['lightning_events']['lightning_mi'] = grouped['lightning_events'].pop('lightning')
        return grouped

    def conversions(self, val, field=None):
        # Convert empty strings to NULL value
        if val == '' or val is None:
            return None
        try:
            # Convert from Unix Epoch time to UTC
            if field == 'lightning_time':
                return datetime.fromtimestamp(int(val), tz=timezone.utc)
            # Convert distance in kilometers to miles
            if field == 'lightning':
                return round(float(val) * 0.621371, 2)
            return val
        except (ValueError, TypeError) as e:
            logger.warning("Conversion failed for field=%s val=%r: %s", field, val, e)
            return None
