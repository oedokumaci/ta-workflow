from pathlib import Path

from ta_workflow.config_parser import YAML_CONFIG

PROJECT_ROOT = Path(YAML_CONFIG.project_root_path)
LOG_PATH: Path = Path(__file__).parents[2] / "logs"
