from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.domains.atmosphere_cycle.repository import atmosphere_repository
from src.domains.atmosphere_cycle.schemas import (
    AtmosphereMode,
    AtmosphereReading,
    AtmosphereReadingCreate,
    AtmosphereStatus,
    MetricAlert,
    MetricTrend,
    OperatingPhase,
)
from src.domains.atmosphere_cycle.thresholds import (
    METRIC_FIELDS,
    assess_reading,
)

SAMPLE_INTERVAL_MINUTES = 10
MISSED_SAMPLES_BEFORE_FAULT = 3
TREND_HORIZON_MINUTES = 30
RATE_PATTERNS_UNAVAILABLE_NOTE = (
    "Rate-based pattern recognition is unavailable with 10-minute manual samples. "
    "CO₂/O₂/VOC rate triggers, persistence windows, and sub-minute transient "
    "filtering are not verified."
)


def create_reading(payload: AtmosphereReadingCreate) -> AtmosphereReading:
    reading = AtmosphereReading(
        id=uuid4().hex,
        **payload.model_dump(),
    )
    atmosphere_repository.create(reading)
    return reading


def _fault_alert(reason: str) -> MetricAlert:
    return MetricAlert(
        metric="sensor_fault",
        label="Sensor / circulation feed",
        value=0,
        unit="status",
        level="alarm",
        threshold=reason,
        priority=-1,
    )


def _get_mode_duration(
    readings: list[AtmosphereReading],
    current_mode: AtmosphereMode,
    now: datetime,
) -> int | None:
    if current_mode == AtmosphereMode.SENSOR_FAULT:
        latest = readings[0] if readings else None
        if latest is None:
            return None
        if not latest.sensors_ok or not latest.circulation_running:
            start = latest.sampled_at
        else:
            start = latest.sampled_at + timedelta(
                minutes=SAMPLE_INTERVAL_MINUTES * MISSED_SAMPLES_BEFORE_FAULT
            )
        return max(0, int((now - start).total_seconds() // 60))

    if not readings:
        return None

    expected_mode = (
        AtmosphereMode.STEADY
        if readings[0].phase == OperatingPhase.STEADY
        else AtmosphereMode.ACCLIMATION
    )
    if current_mode != expected_mode:
        return None

    newest = readings[0]
    start = newest.sampled_at
    previous_timestamp = newest.sampled_at
    for reading in readings[1:]:
        gap = previous_timestamp - reading.sampled_at
        if gap > timedelta(minutes=SAMPLE_INTERVAL_MINUTES * 2):
            break
        if reading.phase != newest.phase or not reading.sensors_ok or not reading.circulation_running:
            break
        start = reading.sampled_at
        previous_timestamp = reading.sampled_at
    return max(0, int((now - start).total_seconds() // 60))


def _make_trends(readings: list[AtmosphereReading]) -> list[MetricTrend]:
    if len(readings) < 2:
        return []

    samples = list(reversed(readings[:4]))
    first = samples[0]
    last = samples[-1]
    elapsed_minutes = (last.sampled_at - first.sampled_at).total_seconds() / 60
    if elapsed_minutes <= 0:
        return []

    trends = []
    for key, (field_name, label, unit) in METRIC_FIELDS.items():
        start_value = getattr(first, field_name)
        end_value = getattr(last, field_name)
        rate_per_minute = (end_value - start_value) / elapsed_minutes
        projected = end_value + rate_per_minute * TREND_HORIZON_MINUTES
        direction = "rising" if rate_per_minute > 0 else "falling" if rate_per_minute < 0 else "stable"
        trends.append(
            MetricTrend(
                metric=key,
                label=label,
                direction=direction,
                current_value=end_value,
                predicted_value=round(projected, 2),
                unit=unit,
            )
        )
    return trends


def get_status(now: datetime | None = None) -> AtmosphereStatus:
    now = now or datetime.now(timezone.utc)
    readings = atmosphere_repository.list_recent()
    latest = readings[0] if readings else None

    if latest is None:
        return AtmosphereStatus(
            site_id=None,
            mode=None,
            phase=None,
            mode_confidence=None,
            mode_duration_minutes=None,
            sampled_at=None,
            feed_status="awaiting_first_reading",
            pattern_detection="unavailable",
            pattern_note=RATE_PATTERNS_UNAVAILABLE_NOTE,
            trend_horizon_minutes=TREND_HORIZON_MINUTES,
            trends=[],
            alerts=[],
            highest_priority_alert=None,
            reading=None,
        )

    site_readings = [reading for reading in readings if reading.site_id == latest.site_id]
    age = now - latest.sampled_at
    missed_sample_limit = timedelta(
        minutes=SAMPLE_INTERVAL_MINUTES * MISSED_SAMPLES_BEFORE_FAULT
    )
    stale = age >= missed_sample_limit
    device_fault = not latest.sensors_ok or not latest.circulation_running
    if device_fault:
        mode = AtmosphereMode.SENSOR_FAULT
        feed_status = "device_fault"
        reason = "Sensor reports fault" if not latest.sensors_ok else "Circulation reported stopped"
        alerts = [_fault_alert(reason)]
    elif stale:
        mode = AtmosphereMode.SENSOR_FAULT
        feed_status = "stale"
        alerts = [_fault_alert("No manual sample for 30 minutes (3 expected intervals)")]
    else:
        mode = (
            AtmosphereMode.STEADY
            if latest.phase == OperatingPhase.STEADY
            else AtmosphereMode.ACCLIMATION
        )
        feed_status = "online_manual"
        alerts = assess_reading(latest)

    highest = alerts[0] if alerts else None
    return AtmosphereStatus(
        site_id=latest.site_id,
        mode=mode,
        phase=latest.phase,
        mode_confidence=None,
        mode_duration_minutes=_get_mode_duration(site_readings, mode, now),
        sampled_at=latest.sampled_at,
        feed_status=feed_status,
        pattern_detection="unavailable",
        pattern_note=RATE_PATTERNS_UNAVAILABLE_NOTE,
        trend_horizon_minutes=TREND_HORIZON_MINUTES,
        trends=_make_trends(site_readings) if feed_status == "online_manual" else [],
        alerts=alerts,
        highest_priority_alert=highest,
        reading=latest,
    )
