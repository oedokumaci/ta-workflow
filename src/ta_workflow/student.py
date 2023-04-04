from pathlib import Path

import pandas as pd  # type: ignore
from pydantic import BaseModel
from unidecode import unidecode

from ta_workflow.config_parser import YAML_CONFIG

PROJECT_ROOT = Path(YAML_CONFIG.project_root_path)


class Student(BaseModel):
    first_name: str
    last_name: str
    department: str
    bilkent_id: str
    email: str
    withdraw_fz: bool


def parse_student_data(resave: bool = True) -> list[Student]:
    try:
        df = pd.read_excel(
            PROJECT_ROOT
            / (YAML_CONFIG.student_data_file_name.split(".")[0] + "_fixed.xlsx")
        )
    except FileNotFoundError:
        if YAML_CONFIG.student_data_file_name.endswith(".csv"):
            df = pd.read_csv(
                PROJECT_ROOT / YAML_CONFIG.student_data_file_name, index_col=0
            )
        elif YAML_CONFIG.student_data_file_name.endswith(".xls"):
            df = pd.read_excel(
                PROJECT_ROOT / YAML_CONFIG.student_data_file_name, index_col=0
            )

    # fix messy column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "")
    )

    # fix data
    df["withdraw_fz"] = df["withdraw_fz"].fillna(False)
    df["first_name"] = df["first_name"].apply(unidecode)
    df["last_name"] = df["last_name"].apply(unidecode)

    if resave:
        df.to_excel(
            PROJECT_ROOT
            / (YAML_CONFIG.student_data_file_name.split(".")[0] + "_fixed.xlsx"),
            index=False,
        )

    students = []
    for row in df.itertuples():
        students.append(Student(**row._asdict()))

    return students


STUDENTS = parse_student_data()
