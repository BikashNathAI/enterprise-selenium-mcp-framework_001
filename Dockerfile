FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    wget curl gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    selenium==4.21.0 \
    webdriver-manager \
    pytest \
    pytest-bdd \
    pytest-xdist \
    pytest-html \
    requests \
    jsonschema \
    pydantic \
    openpyxl \
    faker \
    allure-pytest \
    allure-python-commons \
    python-dotenv \
    PyYAML \
    loguru \
    tenacity \
    anthropic \
    SQLAlchemy \
    pymysql

COPY . .

RUN mkdir -p reports/allure-results screenshots logs \
    data/json data/excel

CMD ["pytest", "tests/api/", "-v", \
     "--html=reports/docker-report.html", \
     "--self-contained-html", "--tb=short"]