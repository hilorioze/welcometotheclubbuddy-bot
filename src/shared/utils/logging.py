import logging


def configure_logging(
    level: int,
    *,
    format: str = "(%(name)s) %(asctime)s | %(levelname)-6s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
):
    logging.captureWarnings(True)  # Enable logging captures warnings issued by warnings.warn()
    logging.basicConfig(
        format=format,
        level=level,
    )
