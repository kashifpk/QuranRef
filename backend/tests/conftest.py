"""Test fixtures for QuranRef integration tests."""

import json
import os
from pathlib import Path

import psycopg
import pytest
from age_orm import Database
from dotenv import dotenv_values
from fastapi.testclient import TestClient

import quranref.db as db_module
from quranref.db import GRAPH_NAME
from quranref.main import app
from quranref.models import Aya, AyaText, HasAya, HasWord, Surah, Text, Word
from quranref.utils import text_to_digest

TEST_DB_NAME = "quranref_test"

# Read connection params from .env.dev (canonical source for local dev)
_env_dev = dotenv_values(Path(__file__).parent.parent.parent / ".env.dev")
DB_HOST = _env_dev.get("DB_HOST", "localhost")
DB_PORT = _env_dev.get("DB_PORT", "5432")
DB_USERNAME = _env_dev.get("DB_USERNAME", "kashif")
DB_PASSWORD = _env_dev.get("DB_PASSWORD", "compulife")

ADMIN_DSN = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
TEST_DSN = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"

META_INFO_DDL = """
CREATE TABLE IF NOT EXISTS meta_info (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL
)
"""

USERS_DDL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    google_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    picture_url TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

# --- Test data ---

ARABIC_TEXTS = {
    "1:1": "بسم الله الرحمن الرحيم",
    "1:2": "الحمد لله رب العالمين",
    "1:3": "الرحمن الرحيم",
    "2:1": "الم",
    "2:2": "ذلك الكتاب لا ريب فيه",
}

ENGLISH_TEXTS = {
    "1:1": "In the name of Allah the Entirely Merciful the Especially Merciful",
    "1:2": "All praise is due to Allah Lord of the worlds",
    "1:3": "The Entirely Merciful the Especially Merciful",
    "2:1": "Alif Lam Meem",
    "2:2": "This is the Book about which there is no doubt",
}


def _seed_test_data(g, db):
    """Seed minimal test data: 2 surahs, 5 ayas, texts, words, edges, meta_info."""

    # 2 Surahs
    surah1 = Surah(
        id="1",
        surah_number=1,
        arabic_name="الفاتحة",
        english_name="Al-Faatiha",
        translated_name="The Opening",
        nuzool_location="Meccan",
        nuzool_order=5,
        rukus=1,
        total_ayas=7,
    )
    surah2 = Surah(
        id="2",
        surah_number=2,
        arabic_name="البقرة",
        english_name="Al-Baqara",
        translated_name="The Cow",
        nuzool_location="Medinan",
        nuzool_order=87,
        rukus=40,
        total_ayas=286,
    )
    g.bulk_add([surah1, surah2])

    # 5 Ayas: 3 from Al-Faatiha, 2 from Al-Baqara
    ayas = []
    for aya_num in range(1, 4):
        ayas.append(Aya(id=f"1:{aya_num}", surah_key="1", aya_number=aya_num))
    for aya_num in range(1, 3):
        ayas.append(Aya(id=f"2:{aya_num}", surah_key="2", aya_number=aya_num))
    g.bulk_add(ayas)

    surah_map = {s.id: s for s in [surah1, surah2]}
    aya_map = {a.id: a for a in ayas}

    # HAS_AYA edges (Surah → Aya)
    has_aya_triples = []
    for aya in ayas:
        surah = surah_map[aya.surah_key]
        has_aya_triples.append((surah, HasAya(), aya))
    g.bulk_add_edges(has_aya_triples)

    # Arabic texts + AYA_TEXT edges
    for aya_id, text in ARABIC_TEXTS.items():
        aya = aya_map[aya_id]
        text_doc = Text(id=text_to_digest(text), text=text)
        g.add(text_doc)
        edge = AyaText(language="arabic", text_type="simple-clean")
        g.connect(aya, edge, text_doc)

    # English texts + AYA_TEXT edges
    for aya_id, text in ENGLISH_TEXTS.items():
        aya = aya_map[aya_id]
        text_doc = Text(id=text_to_digest(text), text=text)
        g.add(text_doc)
        edge = AyaText(language="english", text_type="maududi")
        g.connect(aya, edge, text_doc)

    # Words + HAS_WORD edges (from Arabic texts only)
    word_counts: dict[str, int] = {}
    aya_words: dict[str, set[str]] = {}
    for aya_id, text in ARABIC_TEXTS.items():
        words = text.split(" ")
        aya_words[aya_id] = set(words)
        for w in words:
            word_counts[w] = word_counts.get(w, 0) + 1

    word_objects: dict[str, Word] = {}
    words_to_add = []
    for word_str, count in word_counts.items():
        w = Word.new(word=word_str, count=count)
        words_to_add.append(w)
        word_objects[word_str] = w
    g.bulk_add(words_to_add)

    edge_triples = []
    for aya_id, words in aya_words.items():
        aya = aya_map[aya_id]
        for word_str in words:
            edge_triples.append((aya, HasWord(), word_objects[word_str]))
    g.bulk_add_edges(edge_triples)

    # meta_info table data
    text_types = {"arabic": ["simple-clean"], "english": ["maududi"]}
    with db._pool.connection() as conn:
        conn.execute(
            "INSERT INTO meta_info (key, value) VALUES (%s, %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            ("text-types", json.dumps(text_types)),
        )
        conn.commit()


# --- Fixtures ---


@pytest.fixture(scope="session")
def test_db():
    """Create a test database and return a Database instance."""
    with psycopg.connect(ADMIN_DSN, autocommit=True) as conn:
        conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
        conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")

    db = Database(TEST_DSN)

    # Enable AGE extension
    with db._pool.connection() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS age")
        conn.execute('LOAD \'age\'')
        conn.execute("SET search_path = ag_catalog, \"$user\", public")
        conn.commit()

    yield db

    db._pool.close()
    with psycopg.connect(ADMIN_DSN, autocommit=True) as conn:
        conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")


@pytest.fixture(scope="session")
def test_graph(test_db):
    """Create graph with labels, indexes, seed data."""
    g = test_db.graph(GRAPH_NAME, create=True)

    # Ensure vertex and edge labels
    for vertex_cls in [Surah, Aya, Text, Word]:
        g.ensure_label(vertex_cls)
    for edge_cls in [HasAya, HasWord, AyaText]:
        g.ensure_label(edge_cls, kind="e")

    # Create indexes
    g.create_index(Surah, "id", unique=True)
    g.create_index(Aya, "id", unique=True)
    g.create_index(Aya, "surah_key")
    g.create_index(Text, "id", unique=True)
    g.create_index(Word, "id", unique=True)
    g.create_index(Word, "word")
    g.create_index(Word, "count")

    # Create SQL tables
    with test_db._pool.connection() as conn:
        conn.execute(META_INFO_DDL)
        conn.execute(USERS_DDL)
        conn.commit()

    _seed_test_data(g, test_db)

    yield g


@pytest.fixture(scope="session")
def client(test_db, test_graph):
    """FastAPI TestClient with test database and graph injected."""
    original_db = db_module._db
    db_module._db = test_db

    with TestClient(app) as c:
        yield c

    db_module._db = original_db
