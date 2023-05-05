"""Module for utility functions."""

import logging
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from time import time
from typing import Callable, ParamSpec, TypeVar

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.path import LOG_PATH
from ta_workflow.student import Student, parse_and_validate_student_data

R = TypeVar("R")
P = ParamSpec("P")


def check_log_file_name(log_file_name: str) -> str:
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
        file_name (str): the name of the log file
    """
    log_name = check_log_file_name(log_file_name)
    log_file: Path = LOG_PATH / log_name
    log_file.unlink(missing_ok=True)
    log_file.touch()
    log_formatter = logging.Formatter("%(asctime)s:%(levelname)s: %(message)s")
    log_formatter.datefmt = "%Y-%m-%d %H:%M:%S"

    log_handler = logging.FileHandler(str(log_file))
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)

    std_log_handler = logging.StreamHandler(sys.stdout)
    std_log_handler.setFormatter(log_formatter)
    std_log_handler.setLevel(logging.DEBUG)

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

    message = _mime_init(from_addr, to_addr, subject, body)

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
    STUDENTS: list[Student] = parse_and_validate_student_data()
    HOMEWORKS_SO_FAR = [
        f"Homework_{i}" for i in range(1, YAML_CONFIG.number_of_homeworks + 1)
    ]
    QUIZZES_SO_FAR = [f"Quiz_{i}" for i in range(1, YAML_CONFIG.number_of_quizzes + 1)]
    init_logger()
    return STUDENTS, HOMEWORKS_SO_FAR, QUIZZES_SO_FAR
