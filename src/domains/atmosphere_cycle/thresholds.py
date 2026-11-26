from dataclasses import dataclass

from src.domains.atmosphere_cycle.schemas import OperatingPhase


@dataclass(frozen=True)
class MetricBand:
    key: str
    label: str
    unit: str
    normal_low: float
    normal_high: float
    warning_low: float
    warning_high: float
    lower_alarm: bool = False
    upper_alarm: bool = True
    priority: int = 50


METRIC_FIELDS = {
    "co2": ("co2_ppm", "CO₂", "ppm"),
    "o2": ("o2_percent", "O₂", "vol%"),
    "co": ("co_ppm", "CO", "ppm"),
    "temperature": ("temperature_c", "Temperature", "°C"),
    "humidity": ("humidity_percent", "Relative humidity", "%RH"),
    "pm25": ("pm25_ug_m3", "PM2.5", "μg/m³"),
    "pm10": ("pm10_ug_m3", "PM10", "μg/m³"),
    "tvoc": ("tvoc_ppb", "Total VOC", "ppb"),
}

_STEADY = (
    MetricBand("co2", "CO₂", "ppm", 400, 1200, 400, 2000, lower_alarm=False, priority=0),
    MetricBand("o2", "O₂", "vol%", 19.5, 21.0, 19.0, 22.0, lower_alarm=True, priority=1),
    MetricBand("co", "CO", "ppm", 0, 5, 0, 10, priority=2),
    MetricBand("temperature", "Temperature", "°C", 20, 26, 18, 28, lower_alarm=True, priority=6),
    MetricBand("humidity", "Relative humidity", "%RH", 40, 60, 35, 65, lower_alarm=True, priority=7),
    MetricBand("pm25", "PM2.5", "μg/m³", 0, 15, 0, 35, priority=4),
    MetricBand("pm10", "PM10", "μg/m³", 0, 45, 0, 70, priority=5),
    MetricBand("tvoc", "Total VOC", "ppb", 0, 300, 0, 800, priority=3),
)

_ACCLIMATION = (
    MetricBand("co2", "CO₂", "ppm", 400, 1600, 400, 2500, lower_alarm=False, priority=0),
    MetricBand("o2", "O₂", "vol%", 19.0, 21.5, 18.5, 22.5, lower_alarm=True, priority=1),
    MetricBand("co", "CO", "ppm", 0, 8, 0, 15, priority=2),
    MetricBand("temperature", "Temperature", "°C", 18, 28, 16, 30, lower_alarm=True, priority=6),
    MetricBand("humidity", "Relative humidity", "%RH", 35, 65, 30, 70, lower_alarm=True, priority=7),
    MetricBand("pm25", "PM2.5", "μg/m³", 0, 25, 0, 45, priority=4),
    MetricBand("pm10", "PM10", "μg/m³", 0, 60, 0, 90, priority=5),
    MetricBand("tvoc", "Total VOC", "ppb", 0, 500, 0, 1000, priority=3),
)

BANDS_BY_PHASE = {
    OperatingPhase.STEADY: _STEADY,
    OperatingPhase.ACCLIMATION: _ACCLIMATION,
}


def classify_metric(value: float, band: MetricBand) -> tuple[str, str]:
    if value < band.normal_low:
        if band.lower_alarm and value < band.warning_low:
            return "alarm", f"< {band.warning_low:g}"
        if band.warning_low == band.normal_low:
            return "warning", f"< {band.normal_low:g}"
        return "warning", f"{band.warning_low:g}–{band.normal_low:g}"

    if value <= band.normal_high:
        return "normal", f"{band.normal_low:g}–{band.normal_high:g}"

    if value <= band.warning_high:
        return "warning", f"{band.normal_high:g}–{band.warning_high:g}"

    if band.upper_alarm:
        return "alarm", f"> {band.warning_high:g}"
    return "warning", f"> {band.warning_high:g}"


def assess_reading(reading) -> list:
    from src.domains.atmosphere_cycle.schemas import MetricAlert

    alerts = []
    for band in BANDS_BY_PHASE[reading.phase]:
        field_name, label, unit = METRIC_FIELDS[band.key]
        value = getattr(reading, field_name)
        level, threshold = classify_metric(value, band)
        if level != "normal":
            alerts.append(
                MetricAlert(
                    metric=band.key,
                    label=label,
                    value=value,
                    unit=unit,
                    level=level,
                    threshold=threshold,
                    priority=band.priority,
                )
            )
    return sorted(alerts, key=lambda alert: (alert.level != "alarm", alert.priority))
