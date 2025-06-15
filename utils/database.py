import sqlite3
import csv

from utils.logger import Logger
from dataclasses import dataclass

log = Logger(__name__).get_logger()

@dataclass
class PhrasalVerb:
    def __init__(self, idx, phrasal_verb, translate, example):
        self.idx = idx
        self.phrasal_verb = phrasal_verb
        self.translate = translate
        self.example = example


def create_or_update_phrasal_verbs_table():

    log.info("Creating or updating phrasal_verbs table")

    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS phrasal_verbs (
            idx INTEGER PRIMARY KEY,
            phrasal_verb TEXT,
            translate TEXT,
            example TEXT
        )
        """
    )

    with open("phrasal_varbs.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            cursor.execute(
                "INSERT OR IGNORE INTO phrasal_verbs (idx, phrasal_verb, translate, example) VALUES (?, ?, ?, ?)",
                (row["id"], row["phrasal_verb"], row["translate"], row["example"]),
            )

    log.info("Finished creating or updating phrasal_verbs table")

    conn.commit()
    conn.close()


def get_random_phrasal_verb() -> PhrasalVerb:

    conn = sqlite3.connect("data/db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM phrasal_verbs ORDER BY RANDOM() LIMIT 1")

    result = cursor.fetchone()
    conn.close()

    output = PhrasalVerb(
        idx=result[0],
        phrasal_verb=result[1],
        translate=result[2],
        example=result[3]
    )

    return output



