"""Bookmarks API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .db import get_session
from .dependencies import require_current_user
from .schemas import (
    BookmarkResponse,
    BookmarksListResponse,
    NoteBookmarkRequest,
    NoteBookmarkUpdateRequest,
    ReadingBookmarkRequest,
)
from .sql_models import Bookmark

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("", response_model=BookmarksListResponse)
def list_bookmarks(
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """All bookmarks for the current user."""
    user_id = user["sub"]
    bookmarks = (
        session.query(Bookmark)
        .filter(Bookmark.user_id == user_id)
        .order_by(Bookmark.created_at.desc())
        .all()
    )
    reading = next((b for b in bookmarks if b.bookmark_type == "reading"), None)
    notes = [b for b in bookmarks if b.bookmark_type == "note"]
    return BookmarksListResponse(
        reading=BookmarkResponse.model_validate(reading) if reading else None,
        notes=[BookmarkResponse.model_validate(n) for n in notes],
    )


@router.get("/reading", response_model=BookmarkResponse | None)
def get_reading_bookmark(
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """Get the user's reading position bookmark."""
    user_id = user["sub"]
    bookmark = (
        session.query(Bookmark)
        .filter(Bookmark.user_id == user_id, Bookmark.bookmark_type == "reading")
        .first()
    )
    return bookmark


@router.put("/reading", response_model=BookmarkResponse)
def upsert_reading_bookmark(
    body: ReadingBookmarkRequest,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """Set or replace the reading position bookmark."""
    user_id = user["sub"]
    stmt = (
        insert(Bookmark)
        .values(
            user_id=user_id,
            bookmark_type="reading",
            aya_key=body.aya_key,
            note="",
        )
        .on_conflict_do_update(
            index_elements=["user_id"],
            index_where=Bookmark.bookmark_type == "reading",
            set_=dict(aya_key=body.aya_key, updated_at=text("NOW()")),
        )
        .returning(Bookmark)
    )
    result = session.execute(stmt)
    bookmark = result.scalars().one()
    session.commit()
    session.refresh(bookmark)
    return bookmark


@router.delete("/reading", status_code=204)
def delete_reading_bookmark(
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """Remove the reading position bookmark."""
    user_id = user["sub"]
    bookmark = (
        session.query(Bookmark)
        .filter(Bookmark.user_id == user_id, Bookmark.bookmark_type == "reading")
        .first()
    )
    if bookmark:
        session.delete(bookmark)
        session.commit()


@router.post("/notes", response_model=BookmarkResponse, status_code=201)
def add_note_bookmark(
    body: NoteBookmarkRequest,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """Add a note bookmark."""
    user_id = user["sub"]
    bookmark = Bookmark(
        user_id=user_id,
        bookmark_type="note",
        aya_key=body.aya_key,
        note=body.note,
    )
    session.add(bookmark)
    session.commit()
    session.refresh(bookmark)
    return bookmark


@router.put("/notes/{bookmark_id}", response_model=BookmarkResponse)
def update_note_bookmark(
    bookmark_id: int,
    body: NoteBookmarkUpdateRequest,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """Update a note bookmark's text."""
    user_id = user["sub"]
    bookmark = (
        session.query(Bookmark)
        .filter(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == user_id,
            Bookmark.bookmark_type == "note",
        )
        .first()
    )
    if not bookmark:
        raise HTTPException(status_code=404, detail="Note bookmark not found")
    bookmark.note = body.note
    session.commit()
    session.refresh(bookmark)
    return bookmark


@router.delete("/notes/{bookmark_id}", status_code=204)
def delete_note_bookmark(
    bookmark_id: int,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """Delete a note bookmark."""
    user_id = user["sub"]
    bookmark = (
        session.query(Bookmark)
        .filter(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == user_id,
            Bookmark.bookmark_type == "note",
        )
        .first()
    )
    if not bookmark:
        raise HTTPException(status_code=404, detail="Note bookmark not found")
    session.delete(bookmark)
    session.commit()
