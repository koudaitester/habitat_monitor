# Haptan Monitor

A domain-oriented FastAPI starter for monitoring algae observations.

## Domains

- `haptan_monitor`: records and lists submitted observations in SQLite.
- `algae_vision`: returns an assessment for one of the configured algae categories:
  `normal_chlorella`, `diatom`, `cyanobacteria`, and `other_harmful_algae`.
- `atmosphere_cycle`: records manual air samples and evaluates them against the
  supplied acclimation/steady thresholds.

The assessment endpoint accepts a proposed category and confidence; it does not
analyze image pixels. Connect a validated vision model before treating a category
as an automated identification. Results are screening aids, not laboratory
confirmation or toxin testing.

The Atmosphere Cycle module accepts manual samples for CO₂, O₂, CO, temperature,
relative humidity, PM2.5, PM10, and total VOC. Phase thresholds and metric alarms
are implemented from the supplied project ranges. Samples are expected every
10 minutes; three missed intervals (30 minutes) report a stale feed. The UI
requires an operator to select the acclimation or steady phase.

**Rate-based pattern recognition is intentionally unavailable in manual mode.**
Ten-minute samples cannot verify the supplied 3–5 minute persistence triggers
or reject sub-minute spikes. Accordingly, the module does not claim to detect
rapid CO₂ rise, oxygen depletion, or contaminant accumulation from rates;
confidence is shown as unavailable. Its 30-minute direction estimate is a
straight-line extrapolation from recent samples, not a safety forecast.
Thresholds are project-provided settings, not independently validated life-safety
limits. Do not rely on this prototype as a certified alarm system.
The dashboard displays the supplied threshold reference. For overlapping range
endpoints, the implementation treats the normal-band endpoint as normal and the
alarm boundary as strict; values below a listed minimum are warnings unless a
lower alarm was explicitly supplied.

## Run

```bash
cd habitat_monitor
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn src.main:app --reload
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

The monitor dashboard is available at `http://127.0.0.1:8000`; interactive API
docs are at `http://127.0.0.1:8000/docs`. The SQLite database is created at
`data/haptan_monitor.sqlite3` by default. Set `HAPTAN_DB_PATH` to override it.

## Endpoints

- `GET /health`
- `POST /api/v1/algae-vision/assess`
- `POST /api/v1/monitor/observations`
- `GET /api/v1/monitor/observations?limit=20`
- `POST /api/v1/atmosphere-cycle/readings`
- `GET /api/v1/atmosphere-cycle/status`
- `GET /api/v1/atmosphere-cycle/readings?limit=30`

Example request:

```json
{
  "site_id": "pond-01",
  "algae_type": "cyanobacteria",
  "confidence": 0.87,
  "notes": "Surface sample collected in the morning"
}
```

Run the focused tests with:

```bash
python -m unittest discover -s tests
```
