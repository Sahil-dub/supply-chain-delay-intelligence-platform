# Phase 1: Project Setup

## What We Built

Phase 1 creates the foundation for the project without adding business logic too early. The goal is to make the repository look professional, easy to run, and ready for incremental development.

Included in this phase:

- Repository folder structure for data, SQL, ETL, API, models, dashboards, tests, and documentation.
- Python dependency file for data engineering, API development, testing, and basic modeling.
- Environment variable template for local PostgreSQL and path configuration.
- Docker Compose service for PostgreSQL.
- GitHub Actions workflow for linting and tests.
- Initial README with business problem, target users, architecture, and roadmap.
- A small structure test to keep CI meaningful from the first phase.

## Why This Matters for Data and BI Roles

Hiring teams do not only look for charts or notebooks. They also want to see whether a candidate can structure a project cleanly, document decisions, and make work reproducible.

This phase demonstrates:

- Professional repository organization.
- Awareness of local development environments.
- Early testing and CI habits.
- Clear business framing before technical implementation.

## Suggested Phase 1 Commits

Use 3 to 6 commits so the history feels natural:

```text
chore: initialize project structure
docs: add project overview and business problem
chore: add Python dependencies and environment template
chore: add PostgreSQL docker compose setup
ci: add GitHub Actions workflow for tests
test: verify expected project folders exist
```

## Terminal Commands

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy environment variables:

```powershell
Copy-Item .env.example .env
```

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

Run checks:

```powershell
ruff check .
pytest
```

## Notes for the Next Phase

Phase 2 should add synthetic data generation scripts and raw CSV outputs. It should focus on realistic operational patterns such as supplier reliability differences, warehouse capacity pressure, missing promised delivery dates, and delay reasons.

