import re
from exceptions import InvalidTaskError

FIELD_RE = re.compile(r'(\w+):(\S+)')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def parse_input(raw):
    matches = FIELD_RE.findall(raw)
    if not matches:
        raise InvalidTaskError("No valid fields. Use: title:MyTask priority:high")
    parsed = {k.lower(): v for k, v in matches}
    if "title" not in parsed:
        raise InvalidTaskError("Input must include a 'title' field.")
    return parsed


def is_valid_date(date_str):
    return bool(DATE_RE.match(date_str))
