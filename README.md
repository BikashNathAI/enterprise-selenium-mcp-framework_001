# Enterprise Selenium MCP Framework

Python + Selenium 4 + pytest-bdd + MCP AI Agent

## Quick Start

activate venv first:
venv\Scripts\activate

Run all tests:
pytest tests/ -v

Run smoke tests only:
pytest tests/ -m smoke -v

Run BDD tests:
pytest tests/ui/test_bdd_google.py -v

Run API tests:
pytest tests/api/ -v

Run data-driven tests:
pytest tests/ui/test_data_driven.py -v

Generate HTML report:
pytest tests/ -v --html=reports/test-report.html --self-contained-html

Run parallel:
pytest tests/ -n auto -v

## Framework Structure

config/         - Central configuration
utils/          - Driver, waits, screenshots, DB
pages/          - Page Object Model
features/       - Gherkin BDD feature files
steps/          - BDD step definitions
api/            - REST API client
data/           - Test data (JSON, Excel, Faker)
mcp_agent/      - AI self-healer + test planner
tests/ui/       - Selenium UI tests
tests/api/      - REST API tests
tests/mobile/   - Appium mobile tests
tests/db/       - Database tests
reports/        - HTML and Allure reports

## Test Results

UI Tests         4 passing
BDD Tests        5 passing
API Tests       13 passing
Data-Driven      9 passing
Total           31 passing