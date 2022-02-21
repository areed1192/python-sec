import sys
import logging
import pathlib


def configure_default_logger():
    log_format = '%(asctime)-15s|%(filename)s|%(message)s'
    if not pathlib.Path('logs').exists():
        pathlib.Path('logs').mkdir()
        pathlib.Path('logs/sec_api_log.log').touch()

    if sys.version_info >= (3, 9):

        logging.basicConfig(
            filename="logs/sec_api_log.log",
            level=logging.INFO,
            encoding="utf-8",
            format=log_format
        )

    else:

        logging.basicConfig(
            filename="logs/sec_api_log.log",
            level=logging.INFO,
            encoding="utf-8"
        )


def _lib_logger_factory():
    _logger = logging.getLogger(__package__)
    _logger.addHandler(logging.NullHandler())
    return _logger


logger = _lib_logger_factory()
