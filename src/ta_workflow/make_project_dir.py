import shutil

from ta_workflow.path import PROJECT_ROOT
from ta_workflow.student import Student


def make_project_dir(students: list[Student], assignment_names: list[str]) -> None:
    """
    Creates the project directory structure for each student and assignment.

    Parameters:
    -----------
    students : list of Student objects
        List of students in the class.
    assignment_names : list of str
        List of assignment names.

    Returns:
    --------
    None
    """

    # Iterate over the students and assignments, and create the necessary directories
    for student in students:
        student_dir = PROJECT_ROOT / (student.last_name + "_" + student.bilkent_id)
        student_dir.mkdir(exist_ok=True)
        for assignment in assignment_names:
            assignment_dir = student_dir / assignment
            assignment_dir.mkdir(exist_ok=True)


def delete_project_dir_and_contents(
    students: list[Student], assignment_names: list[str]
) -> None:
    """
    Deletes the project directory structure for each assignment in every student directory.

    Parameters:
    -----------
    students : list of Student objects
        List of students in the class.
    assignment_names : list of str
        List of assignment names.

    Returns:
    --------
    None
    """

    # Iterate over the students and assignments, and delete the necessary directories
    for student in students:
        student_dir = PROJECT_ROOT / (student.last_name + "_" + student.bilkent_id)
        for assignment in assignment_names:
            assignment_dir = student_dir / assignment
            shutil.rmtree(assignment_dir)
