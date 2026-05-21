from pathlib import Path

EXPECTED_DIRECTORIES = [
    "api/routes",
    "api/services",
    "dashboards",
    "data/raw",
    "data/processed",
    "data/sample",
    "docs",
    "notebooks",
    "sql",
    "src/config",
    "src/data_generation",
    "src/database",
    "src/etl",
    "src/features",
    "src/models",
    "src/utils",
    "tests",
]


def test_expected_project_directories_exist() -> None:
    project_root = Path(__file__).resolve().parents[1]

    for directory in EXPECTED_DIRECTORIES:
        assert (project_root / directory).is_dir()

