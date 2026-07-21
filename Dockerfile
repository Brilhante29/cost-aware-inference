FROM python:3.12-slim

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
