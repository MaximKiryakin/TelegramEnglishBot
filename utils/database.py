import sqlite3
import csv

from utils.logger import Logger
from dataclasses import dataclass

log = Logger(__name__).get_logger()


@dataclass
class PhrasalVerb:
    def __init__(self, word_id, phrasal_verb, translate, example):
        self.word_id = word_id
        self.phrasal_verb = phrasal_verb
        self.translate = translate
        self.example = example


def create_or_update_phrasal_verbs_table():
    log.info("Creating or updating phrasal_verbs table")

    conn = sqlite3.connect("data/db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("""DROP TABLE IF EXISTS phrasal_verbs;""")

    cursor.execute(
        """        
        CREATE TABLE phrasal_verbs (
            word_id INTEGER PRIMARY KEY AUTOINCREMENT,
            phrasal_verb TEXT,
            translate TEXT,
            example TEXT
        )
        """
    )

    with open("data/phrasal_varbs.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            cursor.execute(
                "INSERT OR IGNORE INTO phrasal_verbs (word_id, phrasal_verb, translate, example) VALUES (?, ?, ?, ?)",
                (row["id"], row["phrasal_verb"], row["translate"], row["example"]),
            )

    conn.commit()
    conn.close()


def create_users_table():
    log.info("Creating users table")

    conn = sqlite3.connect('data/db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        telegram_user_id BIGINT PRIMARY KEY,
        first_name varchar(100),
        second_name varchar(100)
    )''')

    conn.commit()
    conn.close()


def get_random_phrasal_verb() -> PhrasalVerb:
    conn = sqlite3.connect("data/db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM phrasal_verbs ORDER BY RANDOM() LIMIT 1")

    result = cursor.fetchone()
    conn.close()

    output = PhrasalVerb(
        word_id=result[0],
        phrasal_verb=result[1],
        translate=result[2],
        example=result[3]
    )

    return output


def create_or_update_favorites_table():
    log.info("Creating or updating favorites table")

    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            user_id BIGINT,
            phrasal_verb_id INTEGER,
            PRIMARY KEY user_id
        )
        """
    )

    conn.commit()
    conn.close()


def initialize_database():
    conn = sqlite3.connect('data/db.sqlite3')
    cursor = conn.cursor()

    create_users_table()
    create_or_update_phrasal_verbs_table()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_words (
        telegram_user_id BIGINT,
        word_id INTEGER,
        PRIMARY KEY (telegram_user_id, word_id),
        FOREIGN KEY (telegram_user_id) REFERENCES users(telegram_user_id),
        FOREIGN KEY (word_id) REFERENCES phrasal_verbs(word_id)
    )''')

    conn.commit()
    conn.close()


def add_favorite_word(user_id: int, word_id: str):
    conn = sqlite3.connect('data/db.sqlite3')
    cursor = conn.cursor()

    # Создаем связь
    cursor.execute('''
    INSERT OR IGNORE INTO user_words (telegram_user_id, word_id)
    VALUES (?, ?)''', (user_id, word_id))

    log.info(f"Added favorite word {word_id} for user {user_id}")
    # Добавляем пользователя, если его нет
    cursor.execute('INSERT OR IGNORE INTO users (telegram_user_id) VALUES (?)', (user_id,))

    conn.commit()
    conn.close()
