import logging

import pandas as pd

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.path import PROJECT_ROOT
from ta_workflow.utils import init_logger

pd.set_option("display.max_columns", None)


def get_cols_after(df: pd.DataFrame, col_name: str) -> pd.Index:
    """
    Get the columns after the given column.

    Args:
        df (pd.DataFrame): The dataframe to get the columns from.

    Returns:
        pd.Index: The columns after the given column.
    """
    return df.columns[df.columns.get_loc(col_name) + 1 :]


def summarize_data() -> None:
    init_logger("summary.log")

    config_data = [f"{c}: {getattr(YAML_CONFIG, c)}\n" for c in YAML_CONFIG.__fields__]
    config_data_str = "".join(config_data)
    logging.info("Config file:" + "\n" + config_data_str)

    # Read the student data file into a pandas dataframe
    df: pd.DataFrame = pd.read_excel(
        PROJECT_ROOT
        / (YAML_CONFIG.student_data_file_name.split(".")[0] + "_fixed.xlsx")
    )

    df.set_index("first_name", inplace=True)

    logging.info("Student data file:" + "\n" + str(df) + "\n")

    df_grades = df[get_cols_after(df, "email")]

    logging.info("Summary of the grades:" + "\n" + str(df_grades.describe()) + "\n")
    logging.info(
        "Summary of the grades (zeroes dropped):"
        + "\n"
        + str(df_grades[df_grades != 0].describe())
        + "\n"
    )
