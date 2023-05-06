"""Command line application module."""

import logging

import typer

from ta_workflow.utils import get_students_and_selected_assignments, prepare

app = typer.Typer()

copy_option = typer.Option(
    False,
    help="Copy the files to the students' directories. Default just prints the matches.",
)

score_threshold_argument = typer.Argument(
    35,
    help="The minimum similarity score for a match to be considered valid.",
)

sym_link_option = typer.Option(
    True,
    help="Create a symbolic link of the output excel in the output directory. Original excel is saved in the project root.",
)


@app.command()
def distribute(
    copy: bool = copy_option, score_threshold: int = score_threshold_argument
) -> None:
    """Distribute the assignments into their respective directories."""
    from ta_workflow.distribute_assignments import distribute_assignments

    students, selected_assignments = get_students_and_selected_assignments("distribute")

    try:
        distribute_assignments(students, selected_assignments, copy, score_threshold)
    except FileNotFoundError:
        logging.error(
            "Could not find the assignments directory. Run `make_dirs` first."
        )
    logging.info("Distributing assignments finished.")


@app.command()
def excel(sym_link: bool = sym_link_option) -> None:
    """Create excel files for each assignment to be uploaded to AIRS."""
    from ta_workflow.grades_to_excel import grades_to_excel

    students, selected_assignments = get_students_and_selected_assignments(
        "save to excel"
    )

    grades_to_excel(students, selected_assignments, sym_link)
    logging.info("Creating excel files finished.")


@app.command()
def make_dirs() -> None:
    """Create the directories for each student and assignment. If the directories already exist, it will not overwrite them."""
    from ta_workflow.make_project_dir import make_project_dir

    students, homeworks, quizzes = prepare()

    make_project_dir(students, homeworks + quizzes)
    logging.info("Creating directories finished.")


@app.command()
def split_pdf() -> None:
    """Split a pdf file into individual pages."""
    from ta_workflow.pdf_splitter import get_input, split_pdf

    file_path, pages = get_input()
    split_pdf(file_path, pages)
    print("Splitting pdf finished.")  # logger not initialized for this module
