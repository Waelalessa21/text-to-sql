import json
from pathlib import Path
from typing import Any, List, Tuple


def _cell_value(v: Any) -> Any:
    if v is None:
        return None
    if hasattr(v, "isoformat"):
        return v.isoformat()
    if isinstance(v, (dict, list)):
        return json.dumps(v, default=str)
    return v


try:
    import firebase_admin  # type: ignore
    from firebase_admin import credentials, firestore  # type: ignore
    from google.api_core import exceptions as google_exceptions  # type: ignore

    _FIREBASE_AVAILABLE = True
except ImportError:
    _FIREBASE_AVAILABLE = False
    google_exceptions = None  # type: ignore


class FirebaseManager:
    def __init__(
        self, project_id: str, credentials_path: str, app_name: str | None = None
    ):
        if not _FIREBASE_AVAILABLE:
            raise RuntimeError(
                "firebase-admin is not installed. pip install firebase-admin"
            )
        path = Path(credentials_path)
        if not path.is_absolute():
            path = path.resolve()
        cred = credentials.Certificate(str(path))
        name = app_name or project_id
        try:
            app = firebase_admin.get_app(name)
        except ValueError:
            app = firebase_admin.initialize_app(
                cred, {"projectId": project_id}, name=name
            )
        self._client = firestore.client(app=app)

    def get_schema_text(self) -> str:
        try:
            collections = self._client.collections()
            lines = ["Firestore collections:"]
            for col in collections:
                lines.append(f"  - {col.id}")
            return (
                "\n".join(lines) if len(lines) > 1 else "Firestore collections: (none)"
            )
        except Exception as e:
            if google_exceptions and isinstance(e, google_exceptions.NotFound):
                return (
                    "Firestore is not set up for this project.\n"
                    "Create a Firestore database in Firebase Console:\n"
                    "https://console.firebase.google.com/project/_/firestore"
                )
            return f"Error loading Firestore: {e}"

    def execute_query(self, sql_query: str) -> Tuple[List[str], List[List]]:
        raise NotImplementedError(
            "Firebase/Firestore does not support SQL. Use schema view only."
        )

    def get_collection_documents(
        self, collection_id: str, limit: int = 100
    ) -> Tuple[List[str], List[List]]:
        col_ref = self._client.collection(collection_id)
        docs = col_ref.limit(limit).stream()
        rows = []
        all_keys = set()
        for doc in docs:
            d = doc.to_dict()
            all_keys.update(d.keys())
            rows.append((doc.id, d))
        if not rows:
            return ["id"], []
        keys = ["id"] + sorted(all_keys)
        out_rows = []
        for doc_id, d in rows:
            out_rows.append(
                [doc_id] + [_cell_value(d.get(k)) for k in sorted(all_keys)]
            )
        return keys, out_rows
