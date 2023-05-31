import logging
import os
import subprocess
from pathlib import Path
from smtplib import SMTPSenderRefused
from time import sleep

import pandas as pd  # type: ignore
from unidecode import unidecode

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.path import PROJECT_ROOT
from ta_workflow.student import Student
from ta_workflow.utils import send_email

# to avoid sending too many emails in a short period of time
SEND_EVERY_N_SECONDS = YAML_CONFIG.email_frequency_in_seconds
USER, PASSWORD = os.environ["bilkent_email_credentials"].split(":")
# Read the student data file into a pandas dataframe
df = pd.read_excel(
    PROJECT_ROOT / (YAML_CONFIG.student_data_file_name.split(".")[0] + "_fixed.xlsx")
)


class EmailBody:
    """
    A class to construct different types of email bodies based on the email type.
    """

    def __init__(
        self,
        assignment_name: str,
        student: Student,
        grade: float,
        summary_stats: str,
        ta_name: str = YAML_CONFIG.ta_name,
    ) -> None:
        self.assignment_name = assignment_name
        self.student = student
        self.grade = round(grade, 2)
        self.summary_stats = summary_stats
        self.ta_name = ta_name

    def get_email_body(self) -> str:
        """
        Get the email body for a regular email with attachments.

        Returns:
            str: The email body.
        """
        return f"""Dear {self.student.first_name},

Attached you can find your {self.assignment_name} feedback.
Your grade is {self.grade}.

Here are some summary statistics for {self.assignment_name}:
{self.summary_stats}

Best,

{self.ta_name}
"""

    def get_no_attachment_email_body(self) -> str:
        """
        Get the email body for an email with no attachments.

        Returns:
            str: The email body.
        """
        return f"""Dear {self.student.first_name},

Your grade from {self.assignment_name} is {self.grade}.
It looks like you did not submit any files. If you think this is a mistake, please reply to this email.

Here are some summary statistics for {self.assignment_name}:
{self.summary_stats}

Best,

{self.ta_name}
"""

    def get_large_file_email_body(self) -> str:
        """
        Get the email body for an email with a Google Drive link instead of attachments.

        Returns:
            str: The email body.
        """
        return f"""Dear {self.student.first_name},

Your grade from {self.assignment_name} is {self.grade}.

Here are some summary statistics for {self.assignment_name}:
{self.summary_stats}

Because your files exceed email size limit, they are not attached here. I will send you a drive link with your feedback. Please save the files to your local machine.

Best,

{self.ta_name}
"""


def send_grades(
    students: list[Student],
    assignment_names: list[str],
    user: str = USER,
    password: str = PASSWORD,
    from_addr: str = USER,
    course_code: str = YAML_CONFIG.course_code,
) -> None:
    """
    Send feedback emails to students with their grades and a summary of statistics.

    Args:
        students (list[Student]): A list of
        `Student` objects.
        assignment_names (list[str]): A list of assignment names to send grades for.
        user (str, optional): The email address of the sender. Defaults to USER.
        password (str, optional): The password of the sender. Defaults to PASSWORD.
        from_addr (str, optional): The email address of the sender. Defaults to USER.
        course_code (str, optional): The course code. Defaults to YAML_CONFIG.course_code.

    Returns:
        None
    """
    # Confirm if the user wants to send the emails
    user_input = (
        input(
            f"Do you want to send grades for {', '.join(assignment_names)}? [y/N]: "
        ).lower()
        or "n"
    )
    if user_input != "y":
        return
    # Send emails for each assignment and each student
    for assignment in assignment_names:
        logging.info(f"Sending {assignment} grades...")
        sleep(
            SEND_EVERY_N_SECONDS
        )  # gives time to interrupt the program without sending the first email
        subject = f"{course_code} {assignment.replace('_', ' ')} Feedback"
        summary_stats = (
            df[assignment].describe().round(2)[["mean", "50%", "max"]].to_string()
        )
        for student in students:
            to_addr = [student.email]
            # Get the student's grade for the assignment from the dataframe
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
            # Fix the messy file paths
            for file_path in files_path_messy:
                new_name = unidecode(
                    file_path.name.replace(" ", "_").replace("/", "_").replace("-", "")
                )
                file_path.rename(file_path.parent / new_name)
            # Get the file paths for the attachments
            files_path = [
                str((assignment_dir / f).resolve())
                for f in os.listdir(assignment_dir)
                if f.endswith(".pdf")
            ]
            # Handle cases where there are no files or the files are too large
            if len(files_path) == 0:
                logging.info(
                    f"No pdf files found for {student.email} in {assignment_dir}"
                )
                body = EmailBody(
                    assignment.replace("_", " "), student, student_grade, summary_stats
                ).get_no_attachment_email_body()
                send_email(user, password, from_addr, to_addr, subject, body)
            else:
                try:
                    body = EmailBody(
                        assignment.replace("_", " "),
                        student,
                        student_grade,
                        summary_stats,
                    ).get_email_body()
                    send_email(
                        user, password, from_addr, to_addr, subject, body, files_path
                    )
                    logging.info(f"Email sent successfully to {student.email}")
                except SMTPSenderRefused:
                    logging.error(
                        f"Could not send email to {student.email}, file is too large"
                    )
                    sleep(SEND_EVERY_N_SECONDS)
                    body = EmailBody(
                        assignment.replace("_", " "),
                        student,
                        student_grade,
                        summary_stats,
                    ).get_large_file_email_body()
                    send_email(user, password, from_addr, to_addr, subject, body)
                    # Copy files to Google Drive
                    google_drive_folder = (
                        Path(YAML_CONFIG.google_drive_path).resolve().expanduser()
                        / (student.last_name + "_" + student.bilkent_id)
                        / assignment
                    )
                    google_drive_folder.mkdir(parents=True, exist_ok=True)
                    for file in files_path:
                        subprocess.run(["cp", file, google_drive_folder], check=False)
                    logging.info(f"Files copied to {google_drive_folder}")
            sleep(SEND_EVERY_N_SECONDS)
    logging.info("Done!")
