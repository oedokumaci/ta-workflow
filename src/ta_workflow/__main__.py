"""Entry-point module, in case of using `python -m ta_workflow`."""

import typer

from ta_workflow.cli import main

typer.run(main)
