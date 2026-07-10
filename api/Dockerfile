# Deployment glue only — the API boundary logic lives in
# src/banking_analysis/api/ (ADR 0022) and the SPA source in web/.
# Stage 1 builds the SPA with Node (build-time only); stage 2 is the
# runtime: Python + the built static files. No Node, no CDN, no external
# calls at runtime — the offline constraint holds by construction.

FROM node:20-alpine AS webbuild
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.10-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

COPY src ./src
COPY --from=webbuild /web/dist ./web/dist

ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "banking_analysis.api.runner"]
