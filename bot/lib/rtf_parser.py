import os

from loguru import logger
from striprtf.striprtf import rtf_to_text

WORK_DIR = os.path.curdir


def parse_rtf_header(rtf_text):
    text = rtf_to_text(rtf_text)
    logger.debug(text)
    text = text.strip()[:4000]

    logger.debug(text)

    return text
