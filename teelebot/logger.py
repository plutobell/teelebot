# -*- coding:utf-8 -*-
'''
@creation date: 2019-11-15
@last modification: 2025-05-26
'''
import sys
import inspect
import logging
import threading
from pathlib import Path
from logging.handlers import RotatingFileHandler

_logger = None
_logger_lock = threading.Lock()

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"

COLORS = {
    'WARNING': YELLOW,
    'INFO': CYAN,
    'DEBUG': BLUE,
    'CRITICAL': MAGENTA,
    'ERROR': RED
}

class SequenceFormatter(logging.Formatter):
    _lock = threading.Lock()
    _counter = 0

    def format(self, record):
        with self._lock:
            SequenceFormatter._counter += 1
            seq = SequenceFormatter._counter
        record.seq = seq
        return super().format(record)

class ColoredFormatter(SequenceFormatter):
    def __init__(self, fmt, use_color=True):
        super().__init__(fmt, datefmt="%Y/%m/%d %H:%M:%S")
        self.use_color = use_color

    def format(self, record):
        if self.use_color and record.levelname in COLORS:
            color_seq = COLOR_SEQ % (30 + COLORS[record.levelname])
            original_levelname = record.levelname
            record.levelname = f"{color_seq}{original_levelname}{RESET_SEQ}"
            formatted = super().format(record)
            record.levelname = original_levelname
            return formatted
        else:
            return super().format(record)

def _init_logger(file_log=False, file_log_dir=None):
    global _logger

    logger = logging.getLogger("teelebot")
    logger.setLevel(logging.DEBUG)

    caller_name = inspect.stack()[1].function
    if caller_name == "main":
        logger.handlers.clear()
        _logger = None
    elif _logger is not None:
        return _logger

    use_color = sys.stdout.isatty()
    format_str = "[%(seq)07d][%(asctime)s][%(levelname)s] %(message)s"

    color_formatter = ColoredFormatter(format_str, use_color=use_color)
    file_formatter = logging.Formatter(format_str, datefmt="%Y/%m/%d %H:%M:%S")

    console = logging.StreamHandler()
    console.setFormatter(color_formatter)
    logger.addHandler(console)

    if file_log and file_log_dir:
        log_dir = Path(file_log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "teelebot.log"

        file_handler = RotatingFileHandler(
            filename=log_file,
            mode="a",
            maxBytes=10 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    _logger = logger
    return logger

def get_logger():
    global _logger
    if _logger is None:
        with _logger_lock:
            if _logger is None:
                _init_logger()
    return _logger
