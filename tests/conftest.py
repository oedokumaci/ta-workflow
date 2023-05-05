import logging
from email.mime.multipart import MIMEMultipart
from typing import Generator

import pytest

from ta_workflow.path import LOG_PATH
from ta_workflow.utils import _mime_init, init_logger


@pytest.fixture(scope="package")
def logger_fixture() -> Generator[None, None, None]:
    log_file_path = LOG_PATH / "pytest_test.log"
    init_logger(log_file_path.name)
    yield
    logger = logging.getLogger()
    for handler in logger.handlers:  # close all handlers, Windows fix
        handler.close()
    log_file_path.unlink()


@pytest.fixture(scope="package")
def sample_message() -> MIMEMultipart:
    return _mime_init(
        from_addr="test@example.com",
        to_addr=["test1@example.com", "test2@example.com"],
        subject="Test Subject",
        body="Test Body",
    )
