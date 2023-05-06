"""Command line application module."""

import typer

from ta_workflow.utils import get_students_and_selected_assignments

app = typer.Typer()

copy_option = typer.Option(
    False,
    help="Copy the files to the students' directories. Default just prints the matches.",
)

score_threshold_argument = typer.Argument(
    35,
    help="The minimum similarity score for a match to be considered valid.",
)


@app.command()
def distribute(
    copy: bool = copy_option, score_threshold: int = score_threshold_argument
) -> None:
    """Distribute the assignments into their respective directories."""
    from ta_workflow.distribute_assignments import distribute_assignments

    students, selected_assignments = get_students_and_selected_assignments("distribute")

    distribute_assignments(students, selected_assignments, copy, score_threshold)
