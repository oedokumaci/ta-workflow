import os
import subprocess
from pathlib import Path
from smtplib import SMTPSenderRefused
from time import sleep

import pandas as pd  # type: ignore
from unidecode import unidecode

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.student import Student, parse_student_data
from ta_workflow.utils import send_email

PROJECT_ROOT = Path(YAML_CONFIG.project_root_path)
SEND_EVERY_N_SECONDS = 10  # to avoid too much email error
USER, PASSWORD = os.environ["bilkent_email_credentials"].split(":")


df = pd.read_excel(
    PROJECT_ROOT / (YAML_CONFIG.student_data_file_name.split(".")[0] + "_fixed.xlsx")
)


def get_email_body(
    assignment_name: str, student: Student, grade: float, summary_stats: str
) -> str:
    return f"""Dear {student.first_name},

Attached you can find your {assignment_name} feedback.
Your grade is {grade}/100.

Here are some summary statistics for {assignment_name}:
{summary_stats}

Best,

Ersoy
"""


def get_no_attachment_email_body(
    assignment_name: str, student: Student, grade: float, summary_stats: str
) -> str:
    return f"""Dear {student.first_name},

Your grade from {assignment_name} is {grade}/100.
It looks like you did not submit any files. If you think this is a mistake, please reply to this email.

Here are some summary statistics for {assignment_name}:
{summary_stats}

Best,

Ersoy
"""


def get_large_file_email_body(
    assignment_name: str, student: Student, grade: float, summary_stats: str
) -> str:
    return f"""Dear {student.first_name},

Your grade from {assignment_name} is {grade}/100.

Here are some summary statistics for {assignment_name}:
{summary_stats}

Because your files exceed email size limit, they are not attached here. I will send you a drive link with your feedback. Please save the files to your local machine.

Best,

Ersoy
"""


def send_grades(students: list[Student], assignment_names: list[str]) -> None:
    user = USER
    password = PASSWORD
    from_addr = USER
    for assignment in assignment_names:
        print(f"Sending {assignment} grades...")
        subject = f"{assignment.replace('_', ' ')} Feedback"
        summary_stats = (
            df[assignment].describe().round(2)[["mean", "50%", "max"]].to_string()
        )
        for student in students:
            to_addr = [student.email]
            student_grade = df[df["bilkent_id"] == int(student.bilkent_id)][
                assignment
            ].values[0]
            student_dir = PROJECT_ROOT / (student.last_name + "_" + student.bilkent_id)
            assignment_dir = student_dir / assignment
            files_path_messy = [
                assignment_dir / f
                for f in os.listdir(assignment_dir)
                if f.endswith(".pdf")
            ]
            # fix messy file names
            for file_path in files_path_messy:
                new_name = unidecode(
                    file_path.name.replace(" ", "_").replace("/", "_").replace("-", "")
                )
                file_path.rename(file_path.parent / new_name)
            files_path = [
                str((assignment_dir / f).resolve())
                for f in os.listdir(assignment_dir)
                if f.endswith(".pdf")
            ]
            if len(files_path) == 0:
                print(f"No pdf files found for {student.email} in {assignment_dir}")
                body = get_no_attachment_email_body(
                    assignment.replace("_", " "),
                    student,
                    round(student_grade, 2),
                    summary_stats,
                )
                send_email(user, password, from_addr, to_addr, subject, body)
            else:
                try:
                    print(f"Email sent successfully to {student.email}")
                    body = get_email_body(
                        assignment.replace("_", " "),
                        student,
                        round(student_grade, 2),
                        summary_stats,
                    )
                    send_email(
                        user, password, from_addr, to_addr, subject, body, files_path
                    )
                except SMTPSenderRefused:
                    print(f"Could not send email to {student.email}, file is too large")
                    body = get_large_file_email_body(
                        assignment.replace("_", " "),
                        student,
                        round(student_grade, 2),
                        summary_stats,
                    )
                    send_email(user, password, from_addr, to_addr, subject, body)
                    # copy files to google drive
                    google_drive_folder = (
                        Path(YAML_CONFIG.google_drive_path)
                        / (student.last_name + "_" + student.bilkent_id)
                        / assignment
                    )
                    google_drive_folder.mkdir(parents=True, exist_ok=True)
                    for file in files_path:
                        subprocess.run(["cp", file, google_drive_folder])
            sleep(SEND_EVERY_N_SECONDS)
    print("Done!")


if __name__ == "__main__":
    STUDENTS = parse_student_data()
    HOMEWORKS_SO_FAR = [
        f"Homework_{i}" for i in range(1, YAML_CONFIG.number_of_homeworks + 1)
    ]
    QUIZZES_SO_FAR = [f"Quiz_{i}" for i in range(1, YAML_CONFIG.number_of_quizzes + 1)]
    send_grades(
        STUDENTS, HOMEWORKS_SO_FAR[2:] + QUIZZES_SO_FAR[1:]
    )  # TODO: do not send previously sent grades
