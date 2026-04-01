import json
from collections import defaultdict

from constants import COLUMN_X_THRESHOLD, FOOTER_TOP_THRESHOLD, HEADER_TOP_THRESHOLD


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_textboxes(page):
    return page.get("textboxhorizontal", [])


def get_headers(page):
    return [
        textbox["text"].strip()
        for textbox in get_textboxes(page)
        if textbox["top"] < HEADER_TOP_THRESHOLD
    ]


def is_left_column(textbox):
    return textbox["x0"] < COLUMN_X_THRESHOLD


def is_right_column(textbox):
    return textbox["x0"] >= COLUMN_X_THRESHOLD


def split_columns(page):
    """Split page textboxes into left and right columns, sorted by top."""
    textboxes = [
        textbox for textbox in get_textboxes(page)
        if HEADER_TOP_THRESHOLD <= textbox["top"] < FOOTER_TOP_THRESHOLD
    ]
    left = sorted(
        [textbox for textbox in textboxes if is_left_column(textbox)],
        key=lambda textbox: textbox["top"]
    )
    right = sorted(
        [textbox for textbox in textboxes if is_right_column(textbox)],
        key=lambda textbox: textbox["top"]
    )
    return left, right


def pair_inid_values(column):
    """Group textboxes by top and return (inid_code, value) pairs."""
    groups = defaultdict(list)
    for textbox in column:
        groups[round(textbox["top"], 1)].append(textbox)

    pairs = []
    for top in sorted(groups):
        textboxes = sorted(groups[top], key=lambda textbox: textbox["x0"])
        if len(textboxes) == 2:
            inid, value = textboxes[0], textboxes[1]
            pairs.append((inid["text"].strip(), value["text"].strip()))
    return pairs
