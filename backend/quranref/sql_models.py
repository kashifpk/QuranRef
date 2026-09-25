"""SQLAlchemy models for relational tables (users, meta_info, bookmarks, collections)."""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    google_id: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String, default="")
    picture_url: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))
    last_login: Mapped[datetime] = mapped_column(server_default=text("NOW()"))

    bookmarks: Mapped[list["Bookmark"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    collections: Mapped[list["Collection"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class MetaInfo(Base):
    __tablename__ = "meta_info"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[dict] = mapped_column(JSONB)


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    bookmark_type: Mapped[str] = mapped_column(String)
    aya_key: Mapped[str] = mapped_column(String)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))

    user: Mapped["User"] = relationship(back_populates="bookmarks")

    __table_args__ = (
        CheckConstraint("bookmark_type IN ('reading', 'note')", name="ck_bookmark_type"),
        Index(
            "uq_reading_bookmark",
            "user_id",
            unique=True,
            postgresql_where=text("bookmark_type = 'reading'"),
        ),
        Index("idx_bookmarks_user_id", "user_id"),
    )


class AyaSearch(Base):
    """Denormalized copy of every aya text with a normalized column for searching.

    Rebuilt from the graph by ``quranref-cli post-process build-search-index``.
    """

    __tablename__ = "aya_search"

    id: Mapped[int] = mapped_column(primary_key=True)
    aya_key: Mapped[str] = mapped_column(String)
    language: Mapped[str] = mapped_column(String)
    text_type: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(Text)
    text_norm: Mapped[str] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("aya_key", "language", "text_type", name="uq_aya_search_key"),
        Index("idx_aya_search_lang_type", "language", "text_type"),
        Index(
            "idx_aya_search_norm_trgm",
            "text_norm",
            postgresql_using="gin",
            postgresql_ops={"text_norm": "gin_trgm_ops"},
        ),
    )


class SurahInfo(Base):
    """Descriptive text about a surah in one language (from QUL)."""

    __tablename__ = "surah_info"

    surah_number: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[str] = mapped_column(String, primary_key=True)
    text: Mapped[str] = mapped_column(Text, default="")
    short_text: Mapped[str] = mapped_column(Text, default="")


class Collection(Base):
    """A user's named list of ayas, kept in the order the user chooses."""

    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))

    user: Mapped["User"] = relationship(back_populates="collections")
    items: Mapped[list["CollectionItem"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan",
        order_by="CollectionItem.position, CollectionItem.id",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_collections_user_name"),
        Index("idx_collections_user_id", "user_id"),
    )


class CollectionItem(Base):
    __tablename__ = "collection_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id", ondelete="CASCADE"))
    aya_key: Mapped[str] = mapped_column(String)
    note: Mapped[str] = mapped_column(Text, default="")
    position: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))

    collection: Mapped["Collection"] = relationship(back_populates="items")

    __table_args__ = (
        UniqueConstraint("collection_id", "aya_key", name="uq_collection_items_aya"),
        Index("idx_collection_items_collection_id", "collection_id"),
    )


class TafsirResource(Base):
    """One tafsir (commentary) as imported from a QUL export."""

    __tablename__ = "tafsir_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    language: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String, default="")
    source: Mapped[str] = mapped_column(String, default="")
    license: Mapped[str] = mapped_column(String, default="")


class TafsirText(Base):
    """A passage of commentary and the range of ayas it covers."""

    __tablename__ = "tafsir_texts"

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("tafsir_resources.id", ondelete="CASCADE"))
    from_key: Mapped[str] = mapped_column(String)
    to_key: Mapped[str] = mapped_column(String)
    aya_keys: Mapped[list] = mapped_column(JSONB)
    text: Mapped[str] = mapped_column(Text)

    __table_args__ = (Index("idx_tafsir_texts_resource", "resource_id"),)


class TafsirEntry(Base):
    """Which passage explains which aya (one row per aya per tafsir)."""

    __tablename__ = "tafsir_entries"

    resource_id: Mapped[int] = mapped_column(
        ForeignKey("tafsir_resources.id", ondelete="CASCADE"), primary_key=True
    )
    aya_key: Mapped[str] = mapped_column(String, primary_key=True)
    text_id: Mapped[int] = mapped_column(ForeignKey("tafsir_texts.id", ondelete="CASCADE"))
