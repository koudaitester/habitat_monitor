import os
import sqlite3
from pathlib import Path

from src.domains.atmosphere_cycle.schemas import AtmosphereReading, AtmosphereReadingCreate


DEFAULT_DB_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "haptan_monitor.sqlite3"
)


class AtmosphereRepository:
    def __init__(self, database_path: Path | str):
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS atmosphere_readings (
                    id TEXT PRIMARY KEY,
                    site_id TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    co2_ppm REAL NOT NULL,
                    o2_percent REAL NOT NULL,
                    co_ppm REAL NOT NULL,
                    temperature_c REAL NOT NULL,
                    humidity_percent REAL NOT NULL,
                    pm25_ug_m3 REAL NOT NULL,
                    pm10_ug_m3 REAL NOT NULL,
                    tvoc_ppb REAL NOT NULL,
                    sensors_ok INTEGER NOT NULL,
                    circulation_running INTEGER NOT NULL,
                    sampled_at TEXT NOT NULL
                )
                """
            )

    def create(self, reading: AtmosphereReading) -> None:
        values = reading.model_dump(mode="json")
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO atmosphere_readings (
                    id, site_id, phase, co2_ppm, o2_percent, co_ppm,
                    temperature_c, humidity_percent, pm25_ug_m3, pm10_ug_m3,
                    tvoc_ppb, sensors_ok, circulation_running, sampled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["id"],
                    values["site_id"],
                    values["phase"],
                    values["co2_ppm"],
                    values["o2_percent"],
                    values["co_ppm"],
                    values["temperature_c"],
                    values["humidity_percent"],
                    values["pm25_ug_m3"],
                    values["pm10_ug_m3"],
                    values["tvoc_ppb"],
                    values["sensors_ok"],
                    values["circulation_running"],
                    values["sampled_at"],
                ),
            )

    def list_recent(self, limit: int = 100) -> list[AtmosphereReading]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, site_id, phase, co2_ppm, o2_percent, co_ppm,
                       temperature_c, humidity_percent, pm25_ug_m3, pm10_ug_m3,
                       tvoc_ppb, sensors_ok, circulation_running, sampled_at
                FROM atmosphere_readings
                ORDER BY sampled_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            AtmosphereReading(
                id=row[0],
                site_id=row[1],
                phase=row[2],
                co2_ppm=row[3],
                o2_percent=row[4],
                co_ppm=row[5],
                temperature_c=row[6],
                humidity_percent=row[7],
                pm25_ug_m3=row[8],
                pm10_ug_m3=row[9],
                tvoc_ppb=row[10],
                sensors_ok=bool(row[11]),
                circulation_running=bool(row[12]),
                sampled_at=row[13],
            )
            for row in rows
        ]


atmosphere_repository = AtmosphereRepository(
    os.environ.get("HAPTAN_DB_PATH", DEFAULT_DB_PATH)
)
