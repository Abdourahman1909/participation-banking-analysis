# Deployment glue only — the actual Layer 6 logic lives in
# src/banking_analysis/frontend/. This file's job is just "how do we run
# it," not "what does it do."

FROM python:3.10-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

COPY src ./src

ENV PYTHONPATH=/app/src
EXPOSE 8501
CMD ["uv", "run", "streamlit", "run", "src/banking_analysis/frontend/dashboard.py", "--server.address=0.0.0.0"]
