import traceback
import PIL
from pytesseract import TesseractError

from loguru import logger


# Context Manager that helps to catch and log error when running batch jobs
class SmoothOCRJobRunContext:
    """Context Manager that handles logging and exception handling during single tesseract execution.
       Exceptions raised by jobs can be suppressed.
    """

    def __init__(self, job_info: str = "", suppress_exceptions: bool = True):
        self.job_info = job_info
        self.suppress_exceptions = suppress_exceptions

    def __enter__(self):
        logger.debug(f"Running {self.job_info}.")

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not exc_type:
            return True
        if exc_type in (
                KeyboardInterrupt, BrokenPipeError, ImportError, ChildProcessError, BlockingIOError,
                MemoryError,
                SyntaxError, ModuleNotFoundError, SystemError):
            logger.error(f"Error blocking execution for {self.job_info}")
            logger.debug("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            return False

        if exc_type in (TesseractError, ValueError, PIL.Image.DecompressionBombError):
            logger.info(f"Known Error for {self.job_info}")
            logger.info(f"ERROR VALUE: {exc_value}")
            logger.debug("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            return self.suppress_exceptions

        logger.info(f"Unknown Error blocking execution for {self.job_info}")
        logger.debug("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        return self.suppress_exceptions
