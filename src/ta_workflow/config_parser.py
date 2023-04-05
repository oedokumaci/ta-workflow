"""This module parses and validates the config files in config directory."""

from __future__ import annotations  # needed in 3.9 for | of Python 3.10

from pathlib import Path

import yaml
from pydantic import BaseModel, validator

CONFIG_DIR: Path = Path(__file__).parents[2] / "config"


class YAMLConfig(BaseModel):
    """Parses and validates the contents of config.yaml file.
    Inherits from pydantic BaseModel.
    """

    project_root_path: str
    student_data_file_name: str
    number_of_homeworks: int
    number_of_quizzes: int
    email_frequency_in_seconds: float

    @validator("student_data_file_name")
    def student_data_file_name_must_be_valid(cls, v: str) -> str:
        if not v.endswith(".xls") and not v.endswith(".csv"):
            raise ValueError(
                f"student_data_file_name must be an xls or a csv file, {v} is not"
            )
        return v

    @validator("number_of_homeworks")
    def number_of_homeworks_must_be_valid(cls, v: int) -> int:
        if v < 1:
            raise ValueError(
                f"number_of_homeworks must be a positive integer, {v} is not"
            )
        return v

    @validator("number_of_quizzes")
    def number_of_quizzes_must_be_valid(cls, v: int) -> int:
        if v < 1:
            raise ValueError(
                f"number_of_quizzes must be a positive integer, {v} is not"
            )
        return v

    @validator("email_frequency_in_seconds")
    def email_frequency_in_seconds_must_be_valid(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"email_frequency_in_seconds must be positive, {v} is not")
        return v


def parse_and_validate_configs() -> YAMLConfig:
    """Parses and validates the contents of config files in config directory."""

    # config.yaml
    with open(CONFIG_DIR / "config.yaml") as yaml_file:
        yaml_config: dict[str, str] = yaml.safe_load(yaml_file)
    YAML_CONFIG = YAMLConfig(**yaml_config)

    return YAML_CONFIG


YAML_CONFIG = parse_and_validate_configs()
