from bot.lib.rtf_parser import parse_rtf_header


def check_type(document):
    parsed = parse_rtf_header(document)

