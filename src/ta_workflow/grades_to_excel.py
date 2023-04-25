import subprocess
import sys
from pathlib import Path

import pandas as pd  # type: ignore

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.student import Student, parse_and_validate_student_data

PROJECT_ROOT = Path(YAML_CONFIG.project_root_path)
OS = "windows-based" if sys.platform.startswith("win") else "unix-based"


def grades_to_excel(students: list[Student], assignment_names: list[str]) -> None:
    df = pd.read_excel(
        PROJECT_ROOT
        / (YAML_CONFIG.student_data_file_name.split(".")[0] + "_fixed.xlsx")
    )
    for assignment in assignment_names:
        assignment_data = {}
        for student in students:
            student_grade = df[df["bilkent_id"] == int(student.bilkent_id)][
                assignment
            ].values[0]
            assignment_data[student.bilkent_id] = round(student_grade, 2)
        original = PROJECT_ROOT / f"{assignment}.xls"  # AIRS want .xls not .xlsx
        sym_link = Path(__file__).parents[2] / "outputs" / f"{assignment}.xls"
        pd.DataFrame.from_dict(assignment_data, orient="index").to_excel(
            str(original), header=False
        )
        if OS == "windows-based":
            subprocess.run(["mklink", str(sym_link), str(original)], shell=True)
        else:
            subprocess.run(["ln", "-s", str(original), str(sym_link)], shell=True)


if __name__ == "__main__":
    STUDENTS = parse_and_validate_student_data()
    HOMEWORKS_SO_FAR = [
        f"Homework_{i}" for i in range(1, YAML_CONFIG.number_of_homeworks + 1)
    ]
    QUIZZES_SO_FAR = [f"Quiz_{i}" for i in range(1, YAML_CONFIG.number_of_quizzes + 1)]
    grades_to_excel(STUDENTS, HOMEWORKS_SO_FAR + QUIZZES_SO_FAR)
