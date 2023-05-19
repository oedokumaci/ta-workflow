import logging
import subprocess

from fuzzywuzzy import process  # type: ignore
from unidecode import unidecode

from ta_workflow.path import PROJECT_ROOT
from ta_workflow.student import Student


def distribute_assignments(
    students: list[Student],
    assignment_names: list[str],
    copy: bool = False,
    score_threshold: int = 35,
) -> None:
    """
    Distributes assignments to students based on filename similarity.

    Parameters:
    -----------
    students : list of Student objects
        List of students in the class.
    assignment_names : list of str
        List of assignment names.
    copy : bool, optional
        Whether to copy the files to the students' directories.
    score_threshold : int, optional
        The minimum similarity score required for a match.

    Returns:
    --------
    None
    """

    # Create a dictionary of full names of students mapped to their Student objects
    students_full_names = {
        student.first_name + " " + student.last_name: student for student in students
    }

    # Create a dictionary of students mapped to the number of files they are matched to
    matched_students = {student: 0 for student in students}

    # Iterate over the assignment names and the files in their directories
    for assignment_name in assignment_names:
        assignment_dir = PROJECT_ROOT / assignment_name
        for file in assignment_dir.iterdir():
            if not file.is_file() or not file.name.endswith(".pdf"):
                continue
            # Find the best match for the filename in the dictionary of student full names
            best_match, score = process.extractOne(
                unidecode(file.name), students_full_names.keys()
            )

            # If the similarity score is less than the threshold, log a message and continue to the next file
            if score < score_threshold:
                logging.info(
                    f"Could not find a match for {unidecode(file.name):<41} {'-----':<15} {'-----':<10} Similarity Score: {'--'}"
                )
                continue

            # Get the Student object corresponding to the best match
            best_match_student = students_full_names[best_match]

            # If the Student has not been matched yet, update the matched_students dictionary and log a message
            if matched_students[best_match_student] == 0:
                matched_students[best_match_student] = score
                logging.info(
                    f"Found a match for {unidecode(file.name):<50} {best_match_student.first_name:<15} {best_match_student.last_name:<10} Similarity Score: {score}"
                )

                # If copy is True, copy the file to the Student's directory
                if copy:
                    source_file = str(file)
                    destination_file = str(
                        PROJECT_ROOT
                        / f"{best_match_student.last_name}_{best_match_student.bilkent_id}"
                        / assignment_name
                        / file.name
                    )
                    subprocess.run(
                        [
                            "cp",
                            source_file,
                            destination_file,
                        ],
                        check=True,
                    )

            # If the Student has already been matched, log a message and continue to the next file
            else:
                logging.info(
                    f"{best_match_student.first_name} {best_match_student.last_name} is already matched"
                )
                continue
