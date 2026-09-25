"""CareerOps Local CLI - help only in Phase 1A."""

import typer

__all__ = ["app", "main"]

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def cli() -> None:
    """CareerOps Local - local-first, evidence-based job and contract decision support.

    Decision support only. This tool never applies, messages, logs in, scrapes, or takes any
    external action. Import, assessment, reporting, and tracking commands are deferred to
    later, separately approved phases.
    """


@app.command()
def doctor() -> None:
    """Report environment readiness (deferred in Phase 1A)."""
    typer.echo(
        "careerops doctor: runtime diagnostics are deferred to a later, separately approved "
        "phase. Nothing was inspected: no files, environment variables, external paths, Git "
        "state, secrets, databases, or network resources."
    )


def main() -> None:
    """Console-script entry point."""
    app()
