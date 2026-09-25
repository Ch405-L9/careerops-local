"""CLI is help-only in Phase 1A and must inspect nothing."""

from typer.testing import CliRunner

from careerops.cli.app import app

runner = CliRunner()


def test_root_help_succeeds() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "doctor" in result.output


def test_doctor_help_succeeds() -> None:
    result = runner.invoke(app, ["doctor", "--help"])
    assert result.exit_code == 0


def test_doctor_reports_deferral_and_succeeds() -> None:
    """Refinement: doctor must not exit non-zero and must not scan anything."""
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "deferred" in result.output


def test_only_doctor_is_registered() -> None:
    """Phase 1A exposes no ingestion, assessment, reporting, or tracker command."""
    registered = {command.name or command.callback.__name__ for command in app.registered_commands}
    assert registered == {"doctor"}
