import logging
import subprocess
from pathlib import Path

from fuzzywuzzy import process  # type: ignore
from unidecode import unidecode

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.student import Student

PROJECT_ROOT = Path(YAML_CONFIG.project_root_path)


def distribute_assignments(
    students: list[Student], assignment_names: list[str], copy: bool = False
) -> None:
    students_full_names = {
        student.first_name + " " + student.last_name: student for student in students
    }
    matched_students = {student: 0 for student in students}
    for assignment_name in assignment_names:
        assignment_dir = PROJECT_ROOT / assignment_name
        for file in assignment_dir.iterdir():
            best_match, score = process.extractOne(
                unidecode(file.name), students_full_names.keys()
            )
            best_match_student = students_full_names[best_match]
            if score < 35:
                logging.info(
                    f"Could not find a match for {unidecode(file.name):<41} {'-----':<15} {'-----':<10} Similarity Score: {'--'}"
                )
            else:
                if matched_students[best_match_student] == 0:
                    matched_students[best_match_student] = score
                    logging.info(
                        f"Found a match for {unidecode(file.name):<50} {best_match_student.first_name:<15} {best_match_student.last_name:<10} Similarity Score: {score}"
                    )
                    if copy:
                        subprocess.run(
                            [
                                "cp",
                                file.resolve(),
                                PROJECT_ROOT
                                / (
                                    best_match_student.last_name
                                    + "_"
                                    + best_match_student.bilkent_id
                                )
                                / assignment_name,
                            ]
                        )
                else:
                    logging.info(
                        f"{best_match_student.first_name} {best_match_student.last_name} is already matched"
                    )
