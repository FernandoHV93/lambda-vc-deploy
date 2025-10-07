import logging
from contextlib import suppress

logging.basicConfig(format='%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def printLog(*data):
    with suppress(Exception):
        out = "LOGGING_LOG "
        for d in data:
            out += d.__str__()
        logging.info(out)
        return
    logging.info("BUM ENVVIANDO UN LOG")