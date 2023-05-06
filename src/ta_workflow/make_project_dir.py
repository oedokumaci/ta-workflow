from ta_workflow.path import PROJECT_ROOT
from ta_workflow.student import Student


def make_project_dir(students: list[Student], assignment_names: list[str]) -> None:
    for student in students:
        student_dir = PROJECT_ROOT / (student.last_name + "_" + student.bilkent_id)
        student_dir.mkdir(exist_ok=True)
        for assignment in assignment_names:
            assignment_dir = student_dir / assignment
            assignment_dir.mkdir(exist_ok=True)
