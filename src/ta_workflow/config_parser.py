"""This module parses and validates the config files in config directory."""
from pathlib import Path

import yaml
from pydantic import BaseModel, validator

CONFIG_DIR: Path = Path(__file__).parents[2] / "config"


class YAMLConfig(BaseModel):
    """
    Parses and validates the contents of config.yaml file.
    Inherits from pydantic BaseModel.

    Attributes:
    -----------
    project_root_path : str
        The path to the root directory of the project.
    student_data_file_name : str
        The name of the student data file.
    number_of_homeworks : int
        The number of homework assignments in the course.
    number_of_quizzes : int
        The number of quizzes in the course.
    email_frequency_in_seconds : float
        The frequency (in seconds) at which to send reminder emails.
    google_drive_path : str
        The path to the Google Drive folder for the course.
    course_code : str
        The code for the course.
    ta_name : str
        The name of the TA for the course.
    """

    project_root_path: str
    student_data_file_name: str
    number_of_homeworks: int
    number_of_quizzes: int
    email_frequency_in_seconds: float
    google_drive_path: str
    course_code: str
    ta_name: str

    # Validators to check that the configuration settings are valid
    @validator("student_data_file_name")
    def student_data_file_name_must_be_valid(cls, v: str) -> str:
        if not v.endswith(".xls") and not v.endswith(".csv"):
            raise ValueError(
                f"student_data_file_name must be an xls or a csv file, {v} is not"
            )
        return v

    @validator("number_of_homeworks")
    def number_of_homeworks_must_be_valid(cls, v: int) -> int:
        if v < 0:
            raise ValueError(
                f"number_of_homeworks must be a nonnegative integer, {v} is not"
            )
        return v

    @validator("number_of_quizzes")
    def number_of_quizzes_must_be_valid(cls, v: int) -> int:
        if v < 0:
            raise ValueError(
                f"number_of_quizzes must be a nonnegative integer, {v} is not"
            )
        return v

    @validator("email_frequency_in_seconds")
    def email_frequency_in_seconds_must_be_valid(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"email_frequency_in_seconds must be positive, {v} is not")
        return v

    @validator("course_code")
    def course_code_must_be_valid(cls, v: str) -> str:
        if not v.isidentifier():
            raise ValueError(f"course_code must be a valid identifier, {v} is not")
        elif not v.isupper():
            raise ValueError(f"course_code must be all uppercase, {v} is not")
        return v


def parse_and_validate_configs() -> YAMLConfig:
    """
    Parses and validates the contents of the config file in the config directory.

    Returns:
    --------
    An instance of the YAMLConfig class with the validated configuration settings.
    """

    with open(CONFIG_DIR / "config.yaml") as yaml_file:
        yaml_config: dict[str, str] = yaml.safe_load(yaml_file)
    YAML_CONFIG = YAMLConfig(**yaml_config)  # type: ignore

    return YAML_CONFIG


YAML_CONFIG = parse_and_validate_configs()
