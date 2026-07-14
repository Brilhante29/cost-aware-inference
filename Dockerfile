FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data
COPY benchmarks ./benchmarks

RUN pip install --no-cache-dir .

ENTRYPOINT ["python", "-m", "cost_aware_inference"]
CMD ["benchmark", "--output", "benchmarks/results/cost-aware-baseline.json"]
