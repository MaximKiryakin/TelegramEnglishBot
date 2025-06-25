import aiosqlite
import sqlite3
import csv

from utils.logger import Logger
from dataclasses import dataclass
from typing import List, Optional

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


async def create_or_update_phrasal_verbs_table():
    log.info("Creating or updating phrasal_verbs table")

    async with aiosqlite.connect("data/db.sqlite3") as conn:
        cursor = await conn.cursor()

        await cursor.execute("""DROP TABLE IF EXISTS phrasal_verbs;""")

        await cursor.execute(
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
                await cursor.execute(
                    "INSERT OR IGNORE INTO phrasal_verbs (word_id, phrasal_verb, translate, example) VALUES (?, ?, ?, ?)",
                    (row["id"], row["phrasal_verb"], row["translate"], row["example"]),
                )

        await conn.commit()


async def create_users_table():
    log.info("Creating users table")

    async with aiosqlite.connect('data/db.sqlite3') as conn:
        cursor = await conn.cursor()

        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_user_id BIGINT PRIMARY KEY,
            first_name varchar(100),
            second_name varchar(100),
            fv_use_favourite BOOLEAN DEFAULT FALSE,
            pv_quiz_words_num INTEGER DEFAULT 10
        )''')

        await conn.commit()


async def get_random_phrasal_verbs(num: int = 10) -> List[PhrasalVerb]:
    async with aiosqlite.connect("data/db.sqlite3") as conn:
        cursor = await conn.cursor()

        await cursor.execute(f"SELECT * FROM phrasal_verbs ORDER BY RANDOM() LIMIT {num}")
        result = await cursor.fetchall()

        return [PhrasalVerb(row[0], row[1], row[2], row[3]) for row in result]


async def create_or_update_favorites_table():
    log.info("Creating or updating favorites table")

    async with aiosqlite.connect("data/db.sqlite3") as conn:
        cursor = await conn.cursor()

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS favorites (
                user_id BIGINT,
                phrasal_verb_id INTEGER,
                PRIMARY KEY (user_id, phrasal_verb_id)
            )
            """
        )

        await conn.commit()


async def initialize_database():
    async with aiosqlite.connect('data/db.sqlite3') as conn:
        cursor = await conn.cursor()

        await create_users_table()
        await create_or_update_phrasal_verbs_table()

        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_words (
            telegram_user_id BIGINT,
            word_id INTEGER,
            PRIMARY KEY (telegram_user_id, word_id),
            FOREIGN KEY (telegram_user_id) REFERENCES users(telegram_user_id),
            FOREIGN KEY (word_id) REFERENCES phrasal_verbs(word_id)
        )''')

        await conn.commit()


async def add_favorite_word(user_id: int, word_id: str):
    async with aiosqlite.connect('data/db.sqlite3') as conn:
        cursor = await conn.cursor()

        await cursor.execute('''
        INSERT OR IGNORE INTO user_words (telegram_user_id, word_id)
        VALUES (?, ?)''', (user_id, word_id))

        log.info(f"Added favorite word {word_id} for user {user_id}")
        await cursor.execute('INSERT OR IGNORE INTO users (telegram_user_id) VALUES (?)', (user_id,))

        await conn.commit()


async def get_favorite_words(user_id: int) -> List[PhrasalVerb]:
    async with aiosqlite.connect('data/db.sqlite3') as conn:
        cursor = await conn.cursor()

        await cursor.execute('''
            SELECT 
                user_words.telegram_user_id,
                user_words.word_id,
                phrasal_verbs.phrasal_verb,
                phrasal_verbs.translate,
                phrasal_verbs.example
            FROM user_words
            JOIN phrasal_verbs ON user_words.word_id = phrasal_verbs.word_id
            WHERE user_words.telegram_user_id = ?
        ''', (user_id,))

        result = await cursor.fetchall()
        return [PhrasalVerb(row[1], row[2], row[3], row[4]) for row in result]


async def get_user_info(user_id: int) -> Optional[User]:
    async with aiosqlite.connect("data/db.sqlite3") as conn:
        cursor = await conn.cursor()

        await cursor.execute(
            "SELECT * FROM users WHERE telegram_user_id = ? LIMIT 1;",
            (user_id,)
        )
        result = await cursor.fetchone()

        if result:
            return User(
                telegram_user_id=result[0],
                first_name=result[1],
                second_name=result[2],
                fv_use_favourite=bool(result[3]),
                pv_quiz_words_num=result[4]
            )
        return None


async def update_or_create_user(user: User):
    async with aiosqlite.connect("data/db.sqlite3") as conn:
        await conn.execute("""
            INSERT OR REPLACE INTO users 
            (telegram_user_id, first_name, second_name, fv_use_favourite, pv_quiz_words_num)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user.telegram_user_id,
            user.first_name,
            user.second_name,
            int(user.fv_use_favourite),
            user.pv_quiz_words_num
        ))
        await conn.commit()
