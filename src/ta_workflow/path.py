from pathlib import Path

from ta_workflow.config_parser import YAML_CONFIG

# The root directory of the project
PROJECT_ROOT = Path(YAML_CONFIG.project_root_path)

# The path to the log directory
LOG_PATH: Path = Path(__file__).parents[2] / "logs"
