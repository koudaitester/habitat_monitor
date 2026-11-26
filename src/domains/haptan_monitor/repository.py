import os
import sqlite3
from pathlib import Path

from src.domains.algae_vision.service import assess_category
from src.domains.algae_vision.schemas import AssessmentRequest
from src.domains.haptan_monitor.schemas import Observation, ObservationCreate


DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "data" / "haptan_monitor.sqlite3"


class ObservationRepository:
    def __init__(self, database_path: Path | str):
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS observations (
                    id TEXT PRIMARY KEY,
                    site_id TEXT NOT NULL,
                    algae_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    notes TEXT,
                    observed_at TEXT NOT NULL
                )
                """
            )

    def create(self, observation: Observation) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO observations
                    (id, site_id, algae_type, confidence, notes, observed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    observation.id,
                    observation.site_id,
                    observation.algae_type.value,
                    observation.confidence,
                    observation.notes,
                    observation.observed_at.isoformat(),
                ),
            )

    def list_recent(self, limit: int) -> list[Observation]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, site_id, algae_type, confidence, notes, observed_at
                FROM observations
                ORDER BY observed_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        observations = []
        for row in rows:
            assessment = assess_category(
                AssessmentRequest(algae_type=row[2], confidence=row[3])
            )
            observations.append(
                Observation(
                    id=row[0],
                    site_id=row[1],
                    algae_type=row[2],
                    confidence=row[3],
                    notes=row[4],
                    observed_at=row[5],
                    assessment_level=assessment.assessment_level,
                    summary=assessment.summary,
                )
            )
        return observations


observation_repository = ObservationRepository(
    os.environ.get("HAPTAN_DB_PATH", DEFAULT_DB_PATH)
)
