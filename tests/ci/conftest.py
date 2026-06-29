"""pytest configuration for tests/ci/."""
import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--regen-golden",
        action="store_true",
        default=False,
        help="Regenerate golden fixture files in-place (test_deploy_manifest_snapshot).",
    )
