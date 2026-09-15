FROM python:3.12.14-slim-trixie@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea

RUN apt-get update && apt-get upgrade --yes && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN useradd --create-home --uid 10001 app

COPY --chown=app:app src ./src
COPY --chown=app:app data ./data
COPY --chown=app:app benchmarks ./benchmarks

USER app

ENTRYPOINT ["python", "-m", "cost_aware_inference"]
CMD ["benchmark", "--providers", "local", "--repeat", "5", "--output", "benchmarks/results/cost-aware-baseline.json"]
