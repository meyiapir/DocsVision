import os
from striprtf.striprtf import rtf_to_text

WORK_DIR = os.path.curdir


def parse_rtf_header(rtf_file):
    rtf = rtf_file.read()
    text = rtf_to_text(rtf)
    text = text.strip()[:4000]

    return text
