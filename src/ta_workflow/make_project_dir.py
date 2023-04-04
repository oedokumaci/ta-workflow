from pathlib import Path

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.student import STUDENTS, Student

PROJECT_ROOT = Path(YAML_CONFIG.project_root_path)
HOMEWORKS_SO_FAR = [
    f"Homework_{i}" for i in range(1, YAML_CONFIG.number_of_homeworks + 1)
]


def make_project_dir(students: list[Student], homework_names: list[str]) -> None:
    for student in students:
        student_dir = PROJECT_ROOT / (student.last_name + "_" + student.bilkent_id)
        student_dir.mkdir(exist_ok=True)
        for homework in homework_names:
            homework_dir = student_dir / homework
            homework_dir.mkdir(exist_ok=True)


if __name__ == "__main__":
    make_project_dir(STUDENTS, HOMEWORKS_SO_FAR)
