import logging
import sys

def setup_logging():
    """
    Configures the root logger to output structured logs to the console.
    This setup ensures that all logs from the application are consistently formatted.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        stream=sys.stdout,
    )

    # Optionally, you can set different levels for noisy libraries
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
