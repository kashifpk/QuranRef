"""Test fixtures for QuranRef integration tests."""

import json
import os
from pathlib import Path

import psycopg
import pytest
import quranref.db as db_module
from age_orm import Database
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from quranref.db import GRAPH_NAME
from quranref.main import app
from quranref.models import (
    Aya,
    AyaText,
    ChildOf,
    HasAya,
    HasLemma,
    HasPhrase,
    HasRoot,
    HasTheme,
    HasToken,
    HasTopic,
    HasWord,
    IsForm,
    Lemma,
    Phrase,
    RelatedTopic,
    Root,
    SimilarTo,
    Surah,
    Text,
    Theme,
    Token,
    Topic,
    Word,
)
from quranref.search_index import rebuild_search_index
from quranref.sql_models import Base
from quranref.utils import text_to_digest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_NAME = "quranref_test"

# Read connection params from .env.dev (canonical source for local dev)
_env_dev = dotenv_values(Path(__file__).parent.parent.parent / ".env.dev")


def _env(name: str, default: str) -> str:
    """Environment variable first (CI, other machines), then .env.dev, then default."""
    return os.environ.get(name) or _env_dev.get(name) or default


DB_HOST = _env("DB_HOST", "localhost")
DB_PORT = _env("DB_PORT", "5432")
DB_USERNAME = _env("DB_USERNAME", "kashif")
DB_PASSWORD = _env("DB_PASSWORD", "compulife")

ADMIN_DSN = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
TEST_DSN = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"
TEST_SA_DSN = f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"

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

    # Morphology: tokens for 1:1 and 1:3 with roots, lemmas and English glosses
    roots = {r: Root(id=r, root=r, letters=3) for r in ["سمو", "أله", "رحم"]}
    lemma_specs = {"اسْم": "سمو", "اللَّه": "أله", "رَحْمٰن": "رحم", "رَحِيم": "رحم"}
    lemmas = {lm: Lemma(id=lm, lemma=lm, root=rt, pos="N") for lm, rt in lemma_specs.items()}
    g.bulk_add(list(roots.values()))
    g.bulk_add(list(lemmas.values()))
    token_specs = [
        ("1:1", 1, "بِسْمِ", "بسم", "اسْم", "In (the) name"),
        ("1:1", 2, "ٱللَّهِ", "الله", "اللَّه", "(of) Allah"),
        ("1:1", 3, "ٱلرَّحْمَٰنِ", "الرحمن", "رَحْمٰن", "the Most Gracious"),
        ("1:1", 4, "ٱلرَّحِيمِ", "الرحيم", "رَحِيم", "the Most Merciful"),
        ("1:3", 1, "ٱلرَّحْمَٰنِ", "الرحمن", "رَحْمٰن", "The Most Gracious"),
        ("1:3", 2, "ٱلرَّحِيمِ", "الرحيم", "رَحِيم", "the Especially Merciful"),
    ]
    # 2:1 (الم) is tagged as initials in the corpus: no root, no lemma
    initials = Token(
        id="2:1:1",
        surah_number=2,
        aya_number=1,
        position=1,
        text="الٓمٓ",
        text_simple="الم",
        tag="P",
        features="INL",
        segments=[{"form": "الٓمٓ", "tag": "P", "features": "INL"}],
    )
    tokens = []
    for aya_key, position, text, simple, lemma, gloss in token_specs:
        surah, aya_num = aya_key.split(":")
        tokens.append(
            Token(
                id=f"{aya_key}:{position}",
                surah_number=int(surah),
                aya_number=int(aya_num),
                position=position,
                text=text,
                text_simple=simple,
                tag="N",
                root=lemma_specs[lemma],
                lemma=lemma,
                features=f"ROOT:{lemma_specs[lemma]}|LEM:{lemma}|M|GEN",
                segments=[{"form": text, "tag": "N", "features": f"LEM:{lemma}"}],
                glosses={"english": gloss},
            )
        )
    g.bulk_add(tokens + [initials])
    has_token, has_lemma, is_form = [], [], []
    has_token.append((aya_map["2:1"], HasToken(position=1), initials))
    is_form.append((initials, IsForm(), word_objects["الم"]))
    for token, (aya_key, position, _t, simple, lemma, _g) in zip(tokens, token_specs, strict=True):
        has_token.append((aya_map[aya_key], HasToken(position=position), token))
        has_lemma.append((token, HasLemma(), lemmas[lemma]))
        is_form.append((token, IsForm(), word_objects[simple]))
    has_root = [(lm, HasRoot(), roots[lm.root]) for lm in lemmas.values()]
    # bulk_add_edges takes one edge label per call
    for triples in (has_token, has_lemma, is_form, has_root):
        g.bulk_add_edges(triples)

    # Topics, themes, similar ayas and a recurring phrase
    doctrine = Topic(id="3", name="Doctrine", thematic=True)
    mercy = Topic(id="2", name="Mercy", arabic_name="رحمة", thematic=True, aya_count=1)
    allah = Topic(
        id="1",
        name="Allah",
        arabic_name="الله",
        ontology=True,
        aya_count=2,
        description='<b>Allah</b>, see <topic data-id="2">Mercy</topic>.',
        wiki_link="https://en.wikipedia.org/wiki/Allah",
    )
    g.bulk_add([doctrine, mercy, allah])
    g.bulk_add_edges(
        [(mercy, ChildOf(kind="thematic"), doctrine), (allah, ChildOf(kind="ontology"), doctrine)]
    )
    g.bulk_add_edges([(allah, RelatedTopic(), mercy)])
    g.bulk_add_edges(
        [
            (aya_map["1:1"], HasTopic(), allah),
            (aya_map["1:3"], HasTopic(), allah),
            (aya_map["1:1"], HasTopic(), mercy),
        ]
    )
    theme1 = Theme(id="theme:1", theme="Opening praise", surah_number=1, aya_from=1, aya_to=3)
    theme2 = Theme(
        id="theme:2", theme="The Book", surah_number=2, aya_from=1, aya_to=2, keywords="book"
    )
    g.bulk_add([theme1, theme2])
    g.bulk_add_edges(
        [(aya_map[k], HasTheme(), theme1) for k in ("1:1", "1:2", "1:3")]
        + [(aya_map[k], HasTheme(), theme2) for k in ("2:1", "2:2")]
    )
    g.bulk_add_edges(
        [
            (
                aya_map["1:1"],
                SimilarTo(score=80, coverage=50, matched_words=2, match_words=[[3, 4]]),
                aya_map["1:3"],
            )
        ]
    )
    phrase = Phrase(
        id="phrase:1",
        text="ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
        source_aya="1:1",
        source_from=3,
        source_to=4,
        aya_count=2,
    )
    g.bulk_add([phrase])
    g.bulk_add_edges(
        [
            (aya_map["1:1"], HasPhrase(ranges=[[3, 4]]), phrase),
            (aya_map["1:3"], HasPhrase(ranges=[[1, 2]]), phrase),
        ]
    )

    # Mushaf structure on the ayas, the unit table and surah descriptions
    for aya in ayas:
        aya.juz, aya.hizb, aya.rub, aya.manzil = 1, 1, 1, 1
        aya.ruku = 1 if aya.surah_key == "1" else 2
        aya.surah_ruku = 1
    aya_map["2:2"].sajda = "optional"
    from quranref.graph_bulk import set_vertex_properties

    set_vertex_properties(
        g,
        db,
        "Aya",
        {
            a.id: {
                "juz": a.juz,
                "hizb": a.hizb,
                "rub": a.rub,
                "manzil": a.manzil,
                "ruku": a.ruku,
                "surah_ruku": a.surah_ruku,
                "sajda": a.sajda,
            }
            for a in ayas
        },
    )
    structure = {
        "juz": [
            {
                "number": 1,
                "verses_count": 5,
                "first_verse_key": "1:1",
                "last_verse_key": "2:2",
                "verse_mapping": {"1": "1-3", "2": "1-2"},
            }
        ],
        "hizb": [],
        "rub": [],
        "manzil": [],
        "ruku": [
            {
                "number": 1,
                "surah_ruku_number": 1,
                "verses_count": 3,
                "first_verse_key": "1:1",
                "last_verse_key": "1:3",
                "verse_mapping": {"1": "1-3"},
            }
        ],
    }
    with db._pool.connection() as conn:
        conn.execute(
            "INSERT INTO meta_info (key, value) VALUES (%s, %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            ("structure", json.dumps(structure)),
        )
        for language, text in (
            ("english", "<h2>Name</h2><p>The Opening.</p>"),
            ("urdu", "<p>الفاتحہ</p>"),
        ):
            conn.execute(
                "INSERT INTO surah_info (surah_number, language, text, short_text) VALUES (1, %s, %s, '')",
                (language, text),
            )
        conn.commit()

    # meta_info table data
    text_types = {"arabic": ["simple-clean"], "english": ["maududi"]}
    with db._pool.connection() as conn:
        conn.execute(
            "INSERT INTO meta_info (key, value) VALUES (%s, %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            ("text-types", json.dumps(text_types)),
        )
        conn.commit()

    rebuild_search_index(g, db)


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
        # age-orm puts ag_catalog first in the search path; pin the extension to public
        conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm SCHEMA public")
        conn.execute("LOAD 'age'")
        conn.execute('SET search_path = ag_catalog, "$user", public')
        conn.commit()

    yield db

    db._pool.close()
    with psycopg.connect(ADMIN_DSN, autocommit=True) as conn:
        conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")


@pytest.fixture(scope="session")
def test_engine():
    """Create a SQLAlchemy engine for the test database."""
    engine = create_engine(TEST_SA_DSN)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def test_graph(test_db, test_engine):
    """Create graph with labels, indexes, seed data."""
    g = test_db.graph(GRAPH_NAME, create=True)

    # Ensure vertex and edge labels
    for vertex_cls in [Surah, Aya, Text, Word, Root, Lemma, Token, Topic, Theme, Phrase]:
        g.ensure_label(vertex_cls)
    for edge_cls in [HasAya, HasWord, AyaText, HasToken, HasLemma, HasRoot, IsForm]:
        g.ensure_label(edge_cls, kind="e")
    for edge_cls in [HasTopic, ChildOf, RelatedTopic, HasTheme, SimilarTo, HasPhrase]:
        g.ensure_label(edge_cls, kind="e")

    # Create indexes
    g.create_index(Surah, "id", unique=True)
    g.create_index(Aya, "id", unique=True)
    g.create_index(Aya, "surah_key")
    g.create_index(Text, "id", unique=True)
    g.create_index(Word, "id", unique=True)
    g.create_index(Word, "word")
    g.create_index(Word, "count")

    # Create SQL tables via SQLAlchemy models
    Base.metadata.create_all(test_engine)

    _seed_test_data(g, test_db)

    yield g


@pytest.fixture(scope="session")
def client(test_db, test_graph, test_engine):
    """FastAPI TestClient with test database and graph injected."""
    original_db = db_module._db
    original_engine = db_module._engine
    original_session_factory = db_module._session_factory

    db_module._db = test_db
    db_module._engine = test_engine
    db_module._session_factory = sessionmaker(bind=test_engine)

    with TestClient(app) as c:
        yield c

    db_module._db = original_db
    db_module._engine = original_engine
    db_module._session_factory = original_session_factory
