import re
from typing import TYPE_CHECKING, Tuple

from ai_engine.model.loader import ollama_response  # type: ignore

if TYPE_CHECKING:
    from ai_engine.core.firebase_manager import FirebaseManager  # type: ignore

_FIRESTORE_PROMPT = """You are a Firestore assistant. Given a list of collection names and a user question, reply with ONLY the single collection name to read. One word or two words with underscore. No other text.

Collections: {collections}

User question: {question}

Collection name:"""


def _extract_collection_name(raw: str, valid_ids: set) -> str | None:
    raw = raw.strip().lower()
    for token in re.split(r"[\s,]+", raw):
        token = re.sub(r"[^a-z0-9_]", "", token)
        if token in valid_ids:
            return token
    for cid in valid_ids:
        if cid in raw or raw in cid:
            return cid
    return None


def run_firebase_query(
    user_input: str, firebase_mgr: "FirebaseManager", limit: int = 100
) -> Tuple[str | None, Tuple[list, list] | None, str | None]:
    schema = firebase_mgr.get_schema_text()
    collection_ids = set()
    for ln in schema.splitlines():
        ln = ln.strip()
        if ln.startswith("- "):
            collection_ids.add(ln[2:].strip())
    if not collection_ids:
        return (
            None,
            None,
            "No Firestore collections. Add a collection in Firebase Console.",
        )
    prompt = _FIRESTORE_PROMPT.format(
        collections=", ".join(sorted(collection_ids)),
        question=user_input,
    )
    response = ollama_response(prompt).strip()
    collection_name = _extract_collection_name(response, collection_ids)
    if not collection_name:
        collection_name = (
            next(iter(collection_ids)) if len(collection_ids) == 1 else None
        )
    if not collection_name:
        return (
            None,
            None,
            "Could not pick a collection. Try: " + ", ".join(sorted(collection_ids)),
        )
    try:
        cols, rows = firebase_mgr.get_collection_documents(collection_name, limit=limit)
        return collection_name, (cols, rows), None
    except Exception as e:
        return collection_name, None, str(e)
