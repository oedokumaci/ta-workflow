import logging
import subprocess
import sys
from pathlib import Path

import pandas as pd  # type: ignore

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.path import PROJECT_ROOT
from ta_workflow.student import Student

pd.options.io.excel.xls.writer = (
    "xlwt"  # set the option to 'xlwt' to suppress the .xls warning
)

OS = "windows-based" if sys.platform.startswith("win") else "unix-based"


def grades_to_excel(
    students: list[Student], assignment_names: list[str], sym_link: bool = True
) -> None:
    """
    Creates an Excel file with the grades for each assignment.

    Parameters:
    -----------
    students : list of Student objects
        List of students in the class.
    assignment_names : list of str
        List of assignment names.
    sym_link : bool, optional
        Whether to create a symbolic link to the Excel file in the outputs directory.

    Returns:
    --------
    None
    """

    # Read the fixed student data from the Excel file
    df = pd.read_excel(
        PROJECT_ROOT
        / (YAML_CONFIG.student_data_file_name.split(".")[0] + "_fixed.xlsx")
    )

    # Iterate over the assignment names and create an Excel file for each assignment
    for assignment in assignment_names:
        # Create a dictionary of bilkent IDs mapped to grades for the current assignment
        assignment_data = {}
        for student in students:
            student_grade = df[df["bilkent_id"] == int(student.bilkent_id)][
                assignment
            ].values[0]
            assignment_data[student.bilkent_id] = round(student_grade, 2)

        # Write the dictionary to an Excel file with the assignment name
        original_file = PROJECT_ROOT / f"{assignment}.xls"  # AIRS want .xls not .xlsx
        sym_link_to_original = (
            Path(__file__).parents[2] / "outputs" / f"{assignment}.xls"
        )
        pd.DataFrame.from_dict(assignment_data, orient="index").to_excel(
            str(original_file.resolve()), header=False
        )
        logging.info(f"Created excel for {assignment} at {original_file.resolve()}")

        # If sym_link is True, create a symbolic link to the Excel file in the outputs directory
        if sym_link:
            if OS == "windows-based":
                subprocess.run(
                    [
                        "mklink",
                        str(sym_link_to_original.resolve()),
                        str(original_file.resolve()),
                    ],
                    check=False,
                )
            else:
                subprocess.run(
                    [
                        "ln",
                        "-s",
                        str(original_file.resolve()),
                        str(sym_link_to_original.resolve()),
                    ],
                    check=False,
                )
            logging.info(
                f"Created symbolic link for {assignment} at {sym_link_to_original}"
            )

        # If sym_link is False, log a message indicating that no symbolic link was created
        else:
            logging.info(f"No symbolic link for {assignment} is created")
