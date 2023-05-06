"""Command line application module."""

import typer

from ta_workflow.utils import prepare

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

    students, homeworks, quizzes = prepare()
    assignments = homeworks + quizzes
    selected_assignments = []
    for assignment in assignments:
        if typer.confirm(f"Would you like to distribute {assignment}?"):
            selected_assignments.append(assignment)

    distribute_assignments(students, selected_assignments, copy, score_threshold)
