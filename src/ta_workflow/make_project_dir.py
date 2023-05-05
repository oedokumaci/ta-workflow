from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.path import PROJECT_ROOT
from ta_workflow.student import Student, parse_and_validate_student_data


def make_project_dir(students: list[Student], assignment_names: list[str]) -> None:
    for student in students:
        student_dir = PROJECT_ROOT / (student.last_name + "_" + student.bilkent_id)
        student_dir.mkdir(exist_ok=True)
        for assignment in assignment_names:
            assignment_dir = student_dir / assignment
            assignment_dir.mkdir(exist_ok=True)


if __name__ == "__main__":
    STUDENTS = parse_and_validate_student_data()
    HOMEWORKS_SO_FAR = [
        f"Homework_{i}" for i in range(1, YAML_CONFIG.number_of_homeworks + 1)
    ]
    QUIZZES_SO_FAR = [f"Quiz_{i}" for i in range(1, YAML_CONFIG.number_of_quizzes + 1)]
    make_project_dir(STUDENTS, HOMEWORKS_SO_FAR)
    make_project_dir(STUDENTS, QUIZZES_SO_FAR)
