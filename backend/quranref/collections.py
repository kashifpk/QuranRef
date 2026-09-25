"""Collections API: user curated lists of ayas with optional notes."""

from age_orm import Graph
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .ayatext import ayas_with_texts
from .db import get_session, graph
from .dependencies import require_current_user
from .schemas import (
    AyaPageSchema,
    CollectionDetail,
    CollectionItemRequest,
    CollectionItemResponse,
    CollectionItemUpdateRequest,
    CollectionOrderRequest,
    CollectionRequest,
    CollectionSummary,
    CollectionUpdateRequest,
)
from .sql_models import Collection, CollectionItem

router = APIRouter(prefix="/collections", tags=["collections"])


def _summary(collection: Collection) -> CollectionSummary:
    return CollectionSummary(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        item_count=len(collection.items),
        aya_keys=[item.aya_key for item in collection.items],
        created_at=collection.created_at,
        updated_at=collection.updated_at,
    )


def _owned(session: Session, user_id: int, collection_id: int) -> Collection:
    collection = session.execute(
        select(Collection)
        .options(selectinload(Collection.items))
        .where(Collection.id == collection_id, Collection.user_id == user_id)
    ).scalar_one_or_none()
    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return collection


def _touch(collection: Collection) -> None:
    collection.updated_at = func.now()


@router.get("", response_model=list[CollectionSummary])
def list_collections(
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """The current user's collections, newest first, with the aya keys each one holds."""
    rows = (
        session.execute(
            select(Collection)
            .options(selectinload(Collection.items))
            .where(Collection.user_id == int(user["sub"]))
            .order_by(Collection.updated_at.desc(), Collection.id.desc())
        )
        .scalars()
        .all()
    )
    return [_summary(c) for c in rows]


@router.post("", response_model=CollectionSummary, status_code=status.HTTP_201_CREATED)
def create_collection(
    body: CollectionRequest,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    collection = Collection(
        user_id=int(user["sub"]), name=body.name, description=body.description, items=[]
    )
    session.add(collection)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="A collection with that name exists"
        ) from exc
    session.refresh(collection)
    return _summary(collection)


@router.get("/{collection_id}", response_model=CollectionDetail)
def get_collection(
    collection_id: int,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    return _owned(session, int(user["sub"]), collection_id)


@router.put("/{collection_id}", response_model=CollectionSummary)
def update_collection(
    collection_id: int,
    body: CollectionUpdateRequest,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    collection = _owned(session, int(user["sub"]), collection_id)
    if body.name is not None:
        name = body.name.strip()
        if not name:
            raise HTTPException(status_code=422, detail="name must not be blank")
        collection.name = name
    if body.description is not None:
        collection.description = body.description
    _touch(collection)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="A collection with that name exists"
        ) from exc
    session.refresh(collection)
    return _summary(collection)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: int,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    collection = _owned(session, int(user["sub"]), collection_id)
    session.delete(collection)
    session.commit()


@router.post(
    "/{collection_id}/items",
    response_model=CollectionItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_item(
    collection_id: int,
    body: CollectionItemRequest,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """Append an aya to the collection. 409 when the aya is already in it."""
    collection = _owned(session, int(user["sub"]), collection_id)
    if any(item.aya_key == body.aya_key for item in collection.items):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Aya already in this collection"
        )
    position = max((item.position for item in collection.items), default=-1) + 1
    item = CollectionItem(
        collection_id=collection.id, aya_key=body.aya_key, note=body.note, position=position
    )
    session.add(item)
    _touch(collection)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{collection_id}/items/{item_id}", response_model=CollectionItemResponse)
def update_item(
    collection_id: int,
    item_id: int,
    body: CollectionItemUpdateRequest,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    collection = _owned(session, int(user["sub"]), collection_id)
    item = next((i for i in collection.items if i.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item.note = body.note
    _touch(collection)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{collection_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    collection_id: int,
    item_id: int,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    collection = _owned(session, int(user["sub"]), collection_id)
    item = next((i for i in collection.items if i.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    session.delete(item)
    _touch(collection)
    session.commit()


@router.delete("/{collection_id}/items/by-aya/{aya_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_by_aya(
    collection_id: int,
    aya_key: str,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """Remove an aya from the collection by its key (what the aya menu toggles)."""
    collection = _owned(session, int(user["sub"]), collection_id)
    item = next((i for i in collection.items if i.aya_key == aya_key), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    session.delete(item)
    _touch(collection)
    session.commit()


@router.put("/{collection_id}/order", response_model=CollectionDetail)
def reorder_items(
    collection_id: int,
    body: CollectionOrderRequest,
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
):
    """Set the item order. Items left out of the list keep their relative order at the end."""
    collection = _owned(session, int(user["sub"]), collection_id)
    by_id = {item.id: item for item in collection.items}
    ordered = [by_id[i] for i in body.item_ids if i in by_id]
    seen = {item.id for item in ordered}
    ordered += [item for item in collection.items if item.id not in seen]
    for position, item in enumerate(ordered):
        item.position = position
    _touch(collection)
    session.commit()
    session.expire_all()
    return _owned(session, int(user["sub"]), collection_id)


@router.get("/{collection_id}/ayas", response_model=AyaPageSchema)
def collection_ayas(
    collection_id: int,
    languages: str = Query("arabic:simple"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: dict = Depends(require_current_user),
    session: Session = Depends(get_session),
    g: Graph = Depends(graph),
):
    """The collection's ayas with their texts, in collection order, one page at a time."""
    collection = _owned(session, int(user["sub"]), collection_id)
    keys = [item.aya_key for item in collection.items]
    page = keys[offset : offset + limit]
    return AyaPageSchema(total=len(keys), offset=offset, ayas=ayas_with_texts(g, page, languages))
