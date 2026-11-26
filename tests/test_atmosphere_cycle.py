import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src.domains.atmosphere_cycle.repository import AtmosphereRepository
from src.domains.atmosphere_cycle.schemas import (
    AtmosphereMode,
    AtmosphereReading,
    AtmosphereReadingCreate,
    OperatingPhase,
)
from src.domains.atmosphere_cycle.service import get_status
from src.domains.atmosphere_cycle.thresholds import BANDS_BY_PHASE, classify_metric


def make_reading(sampled_at, **overrides):
    values = {
        "id": f"sample-{sampled_at.timestamp()}",
        "site_id": "habitat-test",
        "phase": OperatingPhase.STEADY,
        "co2_ppm": 800,
        "o2_percent": 20.5,
        "co_ppm": 1,
        "temperature_c": 23,
        "humidity_percent": 50,
        "pm25_ug_m3": 5,
        "pm10_ug_m3": 10,
        "tvoc_ppb": 100,
        "sensors_ok": True,
        "circulation_running": True,
        "sampled_at": sampled_at,
    }
    return AtmosphereReading(**(values | overrides))


class AtmosphereThresholdTests(unittest.TestCase):
    def test_co2_alarm_thresholds_differ_by_phase(self):
        steady_co2 = next(
            band for band in BANDS_BY_PHASE[OperatingPhase.STEADY] if band.key == "co2"
        )
        acclimation_co2 = next(
            band
            for band in BANDS_BY_PHASE[OperatingPhase.ACCLIMATION]
            if band.key == "co2"
        )

        self.assertEqual(classify_metric(2000, steady_co2)[0], "warning")
        self.assertEqual(classify_metric(2000.1, steady_co2)[0], "alarm")
        self.assertEqual(classify_metric(2400, acclimation_co2)[0], "warning")
        self.assertEqual(classify_metric(2500.1, acclimation_co2)[0], "alarm")

    def test_oxygen_boundary_at_alarm_is_warning(self):
        steady_o2 = next(
            band for band in BANDS_BY_PHASE[OperatingPhase.STEADY] if band.key == "o2"
        )

        self.assertEqual(classify_metric(19.0, steady_o2)[0], "warning")
        self.assertEqual(classify_metric(18.99, steady_o2)[0], "alarm")

    def test_sample_timestamp_must_be_timezone_aware_and_not_future(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValueError):
            AtmosphereReadingCreate(
                site_id="habitat-test",
                phase="steady",
                co2_ppm=800,
                o2_percent=20.5,
                co_ppm=1,
                temperature_c=23,
                humidity_percent=50,
                pm25_ug_m3=5,
                pm10_ug_m3=10,
                tvoc_ppb=100,
                sampled_at=datetime.now(),
            )

        with self.assertRaises(ValueError):
            AtmosphereReadingCreate(
                site_id="habitat-test",
                phase="steady",
                co2_ppm=800,
                o2_percent=20.5,
                co_ppm=1,
                temperature_c=23,
                humidity_percent=50,
                pm25_ug_m3=5,
                pm10_ug_m3=10,
                tvoc_ppb=100,
                sampled_at=now + timedelta(minutes=1),
            )


class AtmosphereStatusTests(unittest.TestCase):
    def test_air_alarms_are_sorted_with_co2_first(self):
        now = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = AtmosphereRepository(Path(temp_dir) / "air.sqlite3")
            repository.initialize()
            reading = make_reading(
                now - timedelta(minutes=1),
                co2_ppm=2100,
                o2_percent=18.8,
            )
            repository.create(reading)

            with patch("src.domains.atmosphere_cycle.service.atmosphere_repository", repository):
                status = get_status(now)

        self.assertEqual(status.mode, AtmosphereMode.STEADY)
        self.assertIsNone(status.mode_confidence)
        self.assertEqual(status.highest_priority_alert.metric, "co2")
        self.assertEqual(
            [alert.metric for alert in status.alerts[:2]],
            ["co2", "o2"],
        )
        self.assertEqual(status.pattern_detection, "unavailable")

    def test_feed_faults_after_three_missed_ten_minute_samples(self):
        now = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = AtmosphereRepository(Path(temp_dir) / "air.sqlite3")
            repository.initialize()
            repository.create(make_reading(now - timedelta(minutes=31)))

            with patch("src.domains.atmosphere_cycle.service.atmosphere_repository", repository):
                status = get_status(now)

        self.assertEqual(status.mode, AtmosphereMode.SENSOR_FAULT)
        self.assertEqual(status.feed_status, "stale")
        self.assertEqual(status.highest_priority_alert.metric, "sensor_fault")

    def test_trend_is_linear_thirty_minute_estimate(self):
        now = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = AtmosphereRepository(Path(temp_dir) / "air.sqlite3")
            repository.initialize()
            repository.create(make_reading(now - timedelta(minutes=11), co2_ppm=700))
            repository.create(make_reading(now - timedelta(minutes=1), co2_ppm=900))

            with patch("src.domains.atmosphere_cycle.service.atmosphere_repository", repository):
                status = get_status(now)

        co2_trend = next(trend for trend in status.trends if trend.metric == "co2")
        self.assertEqual(co2_trend.direction, "rising")
        self.assertEqual(co2_trend.predicted_value, 1500)


if __name__ == "__main__":
    unittest.main()
