FROM python:3.10-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

COPY src ./src
COPY scheduler ./scheduler

# Plain HTTP fetcher (curl_cffi) only — no Chromium bundled, since none of
# the banks built so far need JS rendering (ADR 0002's fetcher tiering).
# Add `playwright install-deps chromium && playwright install chromium`
# here only once a bank actually needs DynamicFetcher/StealthyFetcher.

# Runs the full batch pipeline on a schedule (collect → extract → validate),
# ADR 0013. Interval via PIPELINE_INTERVAL_SECONDS.
CMD ["uv", "run", "python", "scheduler/run_pipeline.py"]
