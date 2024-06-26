import pandas as pd
from pydantic import BaseModel, validator
from unidecode import unidecode

from ta_workflow.config_parser import YAML_CONFIG
from ta_workflow.path import PROJECT_ROOT


class Student(BaseModel):
    """
    Represents a student in the system.

    Attributes:
    -----------
    first_name : str
        The first name of the student.
    last_name : str
        The last name of the student.
    department : str
        The department of the student.
    bilkent_id : str
        The unique identifier of the student.
    email : str
        The email address of the student.
    withdraw_fz : bool
        Whether the student has withdrawn from the course.
    """

    # if bilkent_id is int cast it to str before validation with pre=True
    @validator("bilkent_id", pre=True)
    def cast_bilkent_id_to_str(cls, v) -> str:
        return str(v)

    first_name: str
    last_name: str
    department: str
    bilkent_id: str
    email: str
    withdraw_fz: bool

    def __hash__(self) -> int:
        """
        Returns a unique hash value for each instance of the class based on the bilkent_id attribute.
        """
        return hash(self.bilkent_id)


def parse_and_validate_student_data(
    resave: bool = False,
) -> list[Student]:  # resave True for the first time ever use
    """
    Reads the student data from a file and validates it.

    Parameters:
    -----------
    resave : bool, optional
        Whether to save a fixed version of the file.
        Note: Keep this False all the time except for the first time you run the program.

    Returns:
    --------
    A list of Student objects representing the students in the file.
    """

    try:
        # Try to read the fixed Excel file first
        df = pd.read_excel(
            PROJECT_ROOT
            / (YAML_CONFIG.student_data_file_name.split(".")[0] + "_fixed.xlsx")
        )
    except FileNotFoundError:
        # If the fixed Excel file does not exist, try to read the original file
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
        df["withdraw_fz"] = df["withdraw_fz"].fillna(
            False
        )  # Replace NaN values with False for withdraw_fz column
        df["first_name"] = df["first_name"].apply(
            unidecode
        )  # Convert accented characters to ASCII
        df["last_name"] = df["last_name"].apply(unidecode)

        # If resave is True, save the fixed Excel file
        if resave:
            df.to_excel(
                PROJECT_ROOT
                / (YAML_CONFIG.student_data_file_name.split(".")[0] + "_fixed.xlsx"),
                index=False,
            )

    # Create a list of Student objects from the data frame
    return [Student(**row._asdict()) for row in df.itertuples()]  # type: ignore
