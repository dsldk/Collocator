import logging
import time

from os import environ
from pathlib import Path
from functools import wraps
from collections import OrderedDict
from configparser import RawConfigParser


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"{func.__name__} took {end - start:.6f} seconds to complete")
        return result

    return wrapper


class MultiOrderedDict(OrderedDict):
    """ConfigParser that allows multiple entries with same name.

    Ex. print config.get("exif",  "extension")
    ['pdo.so', 'pdo_sqlite.so', 'pdo_mysql.so']
    Based on https://pastebin.com/cZ8SzbXK
    """

    def __setitem__(self, key, value):
        """Allow for multiple entries with same name, using [] notation."""
        if key.endswith("[]"):
            key = key[:-2]
            if isinstance(value, list) and key in self:
                self[key].extend(value)
            else:
                super(OrderedDict, self).__setitem__(key, value)
        else:
            super(MultiOrderedDict, self).__setitem__(key, value)


log_level = environ.get("LOG_LEVEL", "INFO")

# Create a new logger object
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# Check if a StreamHandler has already been added to the logger
console_handler = None
for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        console_handler = handler
        break

# If no StreamHandler was found, create a new one
if console_handler is None:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")
    )
    logger.addHandler(console_handler)

CONFIG = RawConfigParser(dict_type=MultiOrderedDict, strict=False)

current_dir = Path(__file__).resolve().parent
config_file = current_dir / "config.ini"
default_file = current_dir / "default.ini"
CONFIG.read((default_file, config_file))
