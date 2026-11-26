from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class OperatingPhase(str, Enum):
    ACCLIMATION = "acclimation"
    STEADY = "steady"


class AtmosphereMode(str, Enum):
    STEADY = "steady"
    ACCLIMATION = "acclimation"
    CO2_RISE_ALERT = "co2_rise_alert"
    OXYGEN_DEPLETION = "oxygen_depletion"
    CONTAMINANT_ACCUMULATION = "contaminant_accumulation"
    SENSOR_FAULT = "sensor_fault"


class AtmosphereReadingCreate(BaseModel):
    site_id: str = Field(min_length=1, max_length=100)
    phase: OperatingPhase
    co2_ppm: float = Field(ge=0, allow_inf_nan=False)
    o2_percent: float = Field(ge=0, le=100, allow_inf_nan=False)
    co_ppm: float = Field(ge=0, allow_inf_nan=False)
    temperature_c: float = Field(allow_inf_nan=False)
    humidity_percent: float = Field(ge=0, le=100, allow_inf_nan=False)
    pm25_ug_m3: float = Field(ge=0, allow_inf_nan=False)
    pm10_ug_m3: float = Field(ge=0, allow_inf_nan=False)
    tvoc_ppb: float = Field(ge=0, allow_inf_nan=False)
    sensors_ok: bool = True
    circulation_running: bool = True
    sampled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("sampled_at")
    @classmethod
    def require_current_timezone_aware_sample(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("sampled_at must include a timezone")
        if value > datetime.now(timezone.utc):
            raise ValueError("sampled_at cannot be in the future")
        return value.astimezone(timezone.utc)


class AtmosphereReading(AtmosphereReadingCreate):
    id: str


class MetricAlert(BaseModel):
    metric: str
    label: str
    value: float
    unit: str
    level: str
    threshold: str
    priority: int


class MetricTrend(BaseModel):
    metric: str
    label: str
    direction: str
    current_value: float
    predicted_value: float
    unit: str


class AtmosphereStatus(BaseModel):
    site_id: str | None
    mode: AtmosphereMode | None
    phase: OperatingPhase | None
    mode_confidence: float | None
    mode_duration_minutes: int | None
    sampled_at: datetime | None
    feed_status: str
    pattern_detection: str
    pattern_note: str
    trend_horizon_minutes: int
    trends: list[MetricTrend]
    alerts: list[MetricAlert]
    highest_priority_alert: MetricAlert | None
    reading: AtmosphereReading | None
