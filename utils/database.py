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

@dataclass
class User:
    def __init__(self, telegram_user_id, first_name, second_name, fv_use_favourite, pv_quiz_words_num):
        self.telegram_user_id = telegram_user_id
        self.first_name = first_name
        self.second_name = second_name
        self.fv_use_favourite = fv_use_favourite
        self.pv_quiz_words_num = pv_quiz_words_num


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
        second_name varchar(100),
        fv_use_favourite BOOLEAN DEFAULT FALSE,
        pv_quiz_words_num INTEGER DEFAULT 10
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


def get_favorite_words(user_id: int):
    conn = sqlite3.connect('data/db.sqlite3')
    cursor = conn.cursor()

    # Создаем связь
    cursor.execute('''
        SELECT user_words.telegram_user_id, user_words.word_id, phrasal_verbs.phrasal_verb  
        FROM user_words
        JOIN phrasal_verbs ON user_words.word_id = phrasal_verbs.word_id
        WHERE user_words.telegram_user_id = ?
    ''', (user_id, ))

    result = cursor.fetchall()
    conn.close()

    return result


def get_user_info(user_id: int) -> User:

    conn = sqlite3.connect("data/db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users where telegram_user_id = ? LIMIT 1;", (user_id,))

    result = cursor.fetchone()
    conn.close()

    return User(
        telegram_user_id=result[0],
        first_name=result[1],
        second_name=result[2],
        fv_use_favourite=result[3],
        pv_quiz_words_num=result[4]
    )


def update_user_info(user: User):

    conn = sqlite3.connect("data/db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users 
        SET 
            telegram_user_id = ?,
            first_name = ?,
            second_name = ?,
            fv_use_favourite = ?,
            pv_quiz_words_num = ?
        WHERE telegram_user_id = ?;
    """, (
        user.telegram_user_id,
        user.first_name,
        user.second_name,
        user.fv_use_favourite,
        user.pv_quiz_words_num,
        user.telegram_user_id
    ))

    conn.commit()
    conn.close()

