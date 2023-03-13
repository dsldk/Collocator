import logging
import time
from configparser import ConfigParser
from functools import wraps
from os import sep
from os.path import dirname
from typing import Any, Callable


LOCALPATH = dirname(__file__)
if LOCALPATH:
    LOCALPATH += sep
CONFIG = ConfigParser()
CONFIG.read(("%sdefault.ini" % (LOCALPATH,), "%sconfig.ini" % (LOCALPATH,)))

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def timeit(func) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"{func.__name__} took {end - start:.6f} seconds to complete")
        return result

    return wrapper
