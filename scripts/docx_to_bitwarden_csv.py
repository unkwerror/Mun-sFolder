#!/usr/bin/env python3
"""Convert the current one-column DOCX layout into a Bitwarden CSV.

The output is plaintext and contains live secrets. It is created with mode 0600
and must be deleted immediately after a successful import.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
LABEL_PATTERN = re.compile(
    r"^\s*(логин|пароль|id|p|имя пользователя|способ авторизации|oc|"
    r"публичный ip|\*?\s*user|\*?\s*os)\s*:\s*(.*)$",
    re.I | re.S,
)
HEADER = [
    "folder", "favorite", "type", "name", "notes", "fields", "reprompt",
    "login_uri", "login_username", "login_password", "login_totp",
]


def paragraphs(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    result = []
    for paragraph in root.findall(".//w:body/w:p", NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()
        result.append(text)
    return result


def split_records(lines: list[str]) -> list[list[str]]:
    records: list[list[str]] = []
    current: list[str] = []
    has_password = False
    for line in lines:
        if not line:
            if current and has_password:
                records.append(current)
                current, has_password = [], False
            continue
        is_label = bool(LABEL_PATTERN.match(line))
        if current and has_password and not is_label:
            records.append(current)
            current, has_password = [], False
        current.append(line)
        has_password |= bool(re.match(r"^\s*пароль\s*:", line, re.I))
    if current:
        records.append(current)
    return records


def convert(record: list[str], number: int) -> list[str]:
    values: dict[str, str] = {}
    free: list[str] = []
    for line in record:
        match = LABEL_PATTERN.match(line)
        if match:
            values[match.group(1).strip().lower().lstrip("* ")] = match.group(2).strip()
        else:
            free.append(line)

    username = next((values[k] for k in ("логин", "имя пользователя", "user") if k in values), "")
    password = values.get("пароль", "")
    uri = next((line for line in free if re.search(r"https?://|\b(?:\d{1,3}\.){3}\d{1,3}\b", line, re.I)), "")
    if not uri:
        uri = values.get("публичный ip", "")
    name = next((line for line in free if line != uri), "") or f"Imported entry {number}"
    reserved = {"логин", "имя пользователя", "user", "пароль"}
    notes = [line for line in free if line not in {name, uri}]
    notes.extend(f"{key}: {value}" for key, value in values.items() if key not in reserved)
    return ["Imported", "0", "login", name, "\n".join(notes), "", "1", uri, username, password, ""]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = split_records(paragraphs(args.source))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(HEADER)
        writer.writerows(convert(record, index) for index, record in enumerate(records, 1))
    print(f"Created {len(records)} import records in {args.output}")


if __name__ == "__main__":
    main()
