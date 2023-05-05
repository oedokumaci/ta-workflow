"""Command line application module."""

import typer

from ta_workflow.utils import prepare

app = typer.Typer()

copy_option = typer.Option(
    False,
    help="Copy the files to the students' directories. Default just prints the matches.",
)


@app.command()
def distribute(copy: bool = copy_option) -> None:
    """Distribute the assignments."""
    from ta_workflow.distribute_assignments import distribute_assignments

    students, homeworks, quizzes = prepare()
    assignments = homeworks + quizzes
    selected_assignments = []
    for assignment in assignments:
        if typer.confirm(f"Would you like to distribute {assignment}?"):
            selected_assignments.append(assignment)

    distribute_assignments(students, selected_assignments, copy)
