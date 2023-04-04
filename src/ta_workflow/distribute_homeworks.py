import subprocess
from pathlib import Path

from fuzzywuzzy import process  # type: ignore
from unidecode import unidecode

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.student import Student, parse_student_data

PROJECT_ROOT = Path(YAML_CONFIG.project_root_path)


def distribute_homeworks(
    students: list[Student], homework_names: list[str], copy: bool = False
) -> None:
    students_full_names = {
        student.first_name + " " + student.last_name: student for student in students
    }
    matched_students = {student: 0 for student in students}
    for homework in homework_names:
        homework_dir = PROJECT_ROOT / homework
        for file in homework_dir.iterdir():
            best_match, score = process.extractOne(
                unidecode(file.name), students_full_names.keys()
            )
            best_match_student = students_full_names[best_match]
            if score < 35:
                print(f"Could not find a match for {file.name}")
            else:
                if matched_students[best_match_student] == 0:
                    matched_students[best_match_student] = score
                    print(
                        f"Found a match for {file.name}: {best_match_student.first_name} {best_match_student.last_name}, score: {score}"
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
                                / homework,
                            ]
                        )
                else:
                    print(
                        f"{best_match.first_name} {best_match.last_name} is already matched"
                    )


if __name__ == "__main__":
    STUDENTS = parse_student_data()
    HOMEWORKS_SO_FAR = [
        f"Homework_{i}" for i in range(1, YAML_CONFIG.number_of_homeworks + 1)
    ]
    distribute_homeworks(STUDENTS, HOMEWORKS_SO_FAR[:1])
