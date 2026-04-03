from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from NetworkSecurity.logging.logger import logging as logger


class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_details: sys):
        super().__init__(error_message)  # good practice

        self.error_message = error_message
        _, _, exc_tb = error_details.exc_info()

        if exc_tb is not None:
            self.lineno = exc_tb.tb_lineno
            self.filename = exc_tb.tb_frame.f_code.co_filename
        else:
            self.lineno = None
            self.filename = None

    def __str__(self):
        return f"Error occurred in script [{self.filename}] at line number [{self.lineno}] error message [{self.error_message}]"


if __name__ == "__main__":
    try:
        logger.info("Enter the try block")
        a = 1 / 0
        print("This will not be printed", a)
    except Exception as e:
        custom_exception = NetworkSecurityException(e, sys)
        logger.error(str(custom_exception))
        print(custom_exception)
