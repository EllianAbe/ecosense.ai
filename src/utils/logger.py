import logging

logging.basicConfig(
    format=r'[%(asctime)s][%(levelname)s] %(message)s',
    level=logging.INFO
)

logger = logging.getLogger()
