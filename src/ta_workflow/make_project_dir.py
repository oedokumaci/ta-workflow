from pathlib import Path

import pandas as pd  # type: ignore

from ta_workflow.config_parser import YAML_CONFIG

OUTPUTS_DIR: Path = Path(__file__).parents[2] / "outputs"
DATA_DIR: Path = Path(__file__).parents[2] / "data"

print(YAML_CONFIG)

if YAML_CONFIG.student_data_file_name.endswith(".csv"):
    df = pd.read_csv(DATA_DIR / YAML_CONFIG.student_data_file_name)
elif YAML_CONFIG.student_data_file_name.endswith(".xls"):
    df = pd.read_excel(DATA_DIR / YAML_CONFIG.student_data_file_name)
