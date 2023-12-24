"""Module for utility functions."""

import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from time import time
from typing import Callable, ParamSpec, TypeVar

import typer
from rich.logging import RichHandler

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.path import LOG_PATH
from ta_workflow.student import Student, parse_and_validate_student_data

# Define type variables
R = TypeVar("R")
P = ParamSpec("P")


def check_log_file_name(log_file_name: str) -> str:
    """Check if the given log file name is valid and prompt the user to overwrite if necessary.

    Args:
        log_file_name (str): the name of the log file

    Returns:
        str: the valid log file name
    """
    if not log_file_name.endswith(".log") and not log_file_name.endswith(".txt"):
        log_file_name = f"{log_file_name}.log"

    log_file = LOG_PATH / log_file_name
    if log_file.exists():
        user_input = (
            input(f"{log_file_name=!r} already exists, overwrite? y/n (n): ") or "n"
        )
        if user_input != "y":
            new_log_file_name = input("Enter new log file name: ")
            log_file_name = check_log_file_name(new_log_file_name)
    return log_file_name


def init_logger(log_file_name: str = "logs.log") -> None:
    """Initialize the logger.

    Args:
        log_file_name (str): the name of the log file
    """
    # Get the valid log file name
    log_name = check_log_file_name(log_file_name)
    log_file: Path = LOG_PATH / log_name
    # Delete existing log file and create a new one
    log_file.unlink(missing_ok=True)
    log_file.touch()
    # Set up the log formatter
    log_formatter = logging.Formatter("%(asctime)s:%(levelname)s: %(message)s")
    log_formatter.datefmt = "%Y-%m-%d %H:%M:%S"
    # Set up the log handlers
    log_handler = logging.FileHandler(str(log_file))
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)
    # Set the log formatter and handler levels for the standard output
    std_log_formatter = logging.Formatter("%(message)s")
    std_log_formatter.datefmt = "%H:%M:%S"
    std_log_handler = RichHandler()
    std_log_handler.setFormatter(std_log_formatter)
    # Set up the logger
    logger = logging.getLogger()
    logger.addHandler(std_log_handler)
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)
    # Set library logging level to error
    for key in logging.Logger.manager.loggerDict:
        logging.getLogger(key).setLevel(logging.ERROR)
    logging.info(f"Path to log file: {log_file.resolve()}")


def timer_decorator(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator that prints the time it took to execute a function."""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """Wrapper function that prints the time it took to execute a function.

        Returns:
            Any: the result of the function
        """
        t1: float = time()
        result: R = func(*args, **kwargs)
        t2: float = time()
        logging.info(
            f"Method {func.__name__!r} of module {func.__module__!r} executed in {t2 - t1:.4f} seconds."
        )
        return result

    return wrapper


def _mime_init(
    from_addr: str, to_addr: list[str], subject: str, body: str
) -> MIMEMultipart:
    """Initializes the MIME object.

    Args:
        from_addr (str): from address
        to_addr (list[str]): to address
        subject (str): subject of the email
        body (str): body of the email

    Returns:
        MIMEMultipart: MIME object
    """

    message = MIMEMultipart()

    message["From"] = from_addr
    message["To"] = ",".join(to_addr)
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    return message


def send_email(
    user: str,
    password: str,
    from_addr: str,
    to_addr: list[str],
    subject: str,
    body: str,
    files_path: list[str] | None = None,
    server_name: str = "asmtp.bilkent.edu.tr",
) -> None:
    """Sends email to the given recipients.

    Args:
        user (str): username of the email account
        password (str): password of the email account
        from_addr (str): from address
        to_addr (list[str]): to address
        subject (str): subject of the email
        body (str): body of the email
        files_path (list[str] | None, optional): list of file paths to be attached, defaults to None
        server (str, optional): server name, defaults to "asmtp.bilkent.edu.tr"
    """
    # Initialize the MIME object
    message = _mime_init(from_addr, to_addr, subject, body)

    # Attach the files to the email if files_path is not None
    for file_path in files_path or []:
        with open(file_path, "rb") as fp:
            part = MIMEBase("application", "octet-stream")
            part.set_payload((fp).read())
            # Encoding payload is necessary if encoded (compressed) file has to be attached.
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                "attachment; filename= %s" % Path(file_path).name,
            )
            message.attach(part)

    if server_name == "localhost":  # send mail from local server
        # Start local SMTP server
        server = smtplib.SMTP_SSL(server_name)
        text = message.as_string()
        server.send_message(message)
    else:
        # Start SMTP server at port 465
        server = smtplib.SMTP_SSL(server_name, 465)
        server.ehlo()
        # Enter login credentials for the email you want to sent mail from
        server.login(user, password)
        text = message.as_string()
        # Send mail
        server.sendmail(from_addr, to_addr, text)

    server.quit()


def prepare() -> tuple[list[Student], list[str], list[str]]:
    """Prepares the necessary data for the application.

    Returns:
        tuple[list[Student], list[str], list[str]]: a tuple containing a list of Student objects, a list of homework names and a list of quiz names
    """
    # Parse and validate the student data from the CSV file
    STUDENTS: list[Student] = parse_and_validate_student_data()
    # Create a list of homework names and quiz names
    HOMEWORKS_SO_FAR = [
        f"Homework_{i}" for i in range(1, YAML_CONFIG.number_of_homeworks + 1)
    ]
    QUIZZES_SO_FAR = [f"Quiz_{i}" for i in range(1, YAML_CONFIG.number_of_quizzes + 1)]
    init_logger()
    return STUDENTS, HOMEWORKS_SO_FAR, QUIZZES_SO_FAR


def get_students_and_selected_assignments(
    function_job: str,
) -> tuple[list[Student], list[str]]:
    """Prompts the user to select homeworks/quizzes and returns a list of Student objects and a list of selected assignment names.

    Args:
        function_job (str): the job that the function is doing (e.g. grading)

    Returns:
        tuple[list[Student], list[str]]: a tuple containing a list of Student objects and a list of selected assignment names
    """
    # Prepare the necessary data
    students, homeworks, quizzes = prepare()
    assignments = homeworks + quizzes
    selected_assignments = []
    # Prompt the user to select the assignments
    for assignment in assignments:
        if typer.confirm(f"Do you want to {function_job} {assignment}?"):
            selected_assignments.append(assignment)
    return students, selected_assignments
