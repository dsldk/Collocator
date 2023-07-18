"""Load ngrams from json and make them searchable."""

import json
import os
import sqlite3
import tempfile
from pathlib import Path

from collocator import logger, timeit, CONFIG


async def load_all_models() -> dict:
    """Load all models from config."""
    models = {}
    for model_name in CONFIG.get("general", "models").split(","):
        source_file = os.path.join(
            CONFIG.get("general", "data_dir"), CONFIG.get(model_name, "source_file")
        )
        ngrams = await load_ngrams(source_file)
        connection = await store_ngrams_in_database(ngrams, model_name, force_new=True)
        models[model_name] = {
            "title": CONFIG.get(model_name, "title"),
            "description": CONFIG.get(model_name, "description"),
            "connection": connection,
            "delimiter": ngrams.get("delimiter", "_"),
            "min_count": ngrams.get("min_count", 0.0),
            "threshold": ngrams.get("threshold", 0.0),
            "size": ngrams.get("size", 0),
            "scorer": ngrams.get("scorer", "n/a"),
        }

    return models


@timeit
async def load_ngrams(source_file: str) -> dict:
    """Load ngrams from json file."""
    logger.info("Loading ngrams from %s", source_file)
    # Determine relative path to source file
    source_file = str(Path(__file__).parent.resolve() / source_file)
    with open(source_file, "r") as f:
        ngrams = json.load(f)
    return ngrams


@timeit
async def store_ngrams_in_database(
    ngrams: dict, model_name: str, force_new: bool = False
) -> sqlite3.Connection:
    """Store ngrams in a sqlite database in temporary dir."""
    tempdir = tempfile.gettempdir()
    database_file = f"{tempdir}/ngrams_{model_name}.db"

    # Create a temporary database
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()

    # Is the database empty?
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    if cur.fetchall():
        # Count number of rows in ngrams table
        cur.execute("SELECT COUNT(*) FROM ngrams")
        if cur.fetchone()[0] == 0:
            force_new = True
    if not force_new:
        logger.info("Using existing database %s", database_file)
        return conn

    logger.info(f"Creating database {database_file}")
    # Create table for ngrams wiit id, ngram, score and length of ngram
    cur.execute("DROP TABLE IF EXISTS ngrams")
    cur.execute(
        "CREATE TABLE ngrams (id INTEGER PRIMARY KEY AUTOINCREMENT, ngram TEXT, length INTEGER, score FLOAT)"
    )
    # Create table for words with id, word, ngram_id, and position
    cur.execute("DROP TABLE IF EXISTS words")
    cur.execute(
        "CREATE TABLE words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT, ngram_id INTEGER, position INTEGER)"
    )

    delimiter = ngrams.get("delimiter", "_")
    # Insert ngrams into database
    for ngram, score in ngrams.get("phrasegrams", {}).items():
        # Split ngram into words
        words = ngram.split(delimiter)
        # Insert ngram into ngrams table
        cur.execute(
            "INSERT INTO ngrams (ngram, length, score) VALUES (?, ?, ?)",
            (ngram, len(words), score),
        )
        # Get id of inserted ngram
        ngram_id = cur.lastrowid
        # Insert words into words table
        for position, word in enumerate(words):
            cur.execute(
                "INSERT INTO words (word, ngram_id, position) VALUES (?, ?, ?)",
                (word, ngram_id, position),
            )
    cur.close()
    return conn


@timeit
async def search_ngrams(
    word: str, conn: sqlite3.Connection, threshold: float = 0.0
) -> dict:
    """Search the ngrams database for a word."""
    cur = conn.cursor()
    cur.execute(
        "SELECT w.word, w.position, n.ngram, n.length, n.score FROM ngrams n, words w WHERE n.id = w.ngram_id AND w.word = ?",
        (word,),
    )
    # Handle threshold
    result = [
        (word, position, ngram, length, score)
        for word, position, ngram, length, score in cur.fetchall()
        if score >= threshold
    ]

    # Sort by score
    result.sort(key=lambda x: x[4], reverse=True)

    # Split into left, right and in contexts
    ngrams = {"left": [], "right": [], "in": []}
    for word, position, ngram, length, score in result:
        if position == 0:
            ngrams["right"].append((ngram, score))
        elif position == length - 1:
            ngrams["left"].append((ngram, score))
        else:
            ngrams["in"].append((ngram, score))
    return ngrams


if __name__ == "__main__":
    import sys

    ngrams = load_ngrams(sys.argv[1])
    conn = store_ngrams_in_database(ngrams)

    for word in sys.argv[2:]:
        result = search_ngrams(word, conn)
        print(result)
