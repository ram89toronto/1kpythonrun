"""Command-line app to query people data from a CSV hosted online.

The CSV is available at:
https://pythonhow.com/media/django-summernote/2025-06-09/69f2a74b-0950-425d-a1a4-0ce0afe9b755.csv

The program downloads the CSV, reads the records and allows querying by a person's name.
It then prints the person's age and city if found.
Usage:
    python 31.py [name]
If no name is provided as a command-line argument, the user is prompted to enter one.
"""
import csv
import sys
from typing import List, Dict, Tuple

import requests

DATA_URL = (
    "https://pythonhow.com/media/django-summernote/2025-06-09/"
    "69f2a74b-0950-425d-a1a4-0ce0afe9b755.csv"
)


def fetch_csv(url: str = DATA_URL) -> List[Dict[str, str]]:
    """Download the CSV from *url* and return a list of row dictionaries."""
    response = requests.get(url)
    response.raise_for_status()
    text = response.text
    reader = csv.DictReader(text.splitlines())
    return list(reader)


def query_by_name(rows: List[Dict[str, str]], name: str) -> Tuple[str, str]:
    """Return the age and city for *name* if found; otherwise ("", "")."""
    name = name.strip().lower()
    for row in rows:
        if row.get("name", "").strip().lower() == name:
            return row.get("age", ""), row.get("city", "")
    return "", ""


def main(argv: List[str] = None) -> None:
    argv = argv or sys.argv[1:]
    rows = fetch_csv()
    if argv:
        name = " ".join(argv)
    else:
        name = input("Enter a name to look up: ")
    age, city = query_by_name(rows, name)
    if age and city:
        print(f"{name} is {age} years old and lives in {city}.")
    else:
        print(f"No data found for '{name}'.")


if __name__ == "__main__":
    main()
