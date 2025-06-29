import logging

import colorlog

# Create a formatter for the file logs
file_formatter = logging.Formatter(
    "[%(asctime)s] [%(filename)s %(lineno)d %(levelname)s] %(message)s",
    datefmt="%m-%d %H:%M:%S"
)

# Create a file handler
file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_formatter)

# Create a formatter for colorized logs
color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s[%(asctime)s] [%(filename)s %(lineno)d %(levelname)s] %(message)s",
    datefmt="%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "white",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(color_formatter)

# Set up the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

if __name__ == "__main__":
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
