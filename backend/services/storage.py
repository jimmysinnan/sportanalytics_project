from __future__ import annotations
import asyncio
import io
import os
import uuid

from PIL import Image

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "orbyon-photos")
MAX_PHOTO_SIDE = 800


def resize_photo(data: bytes) -> bytes:
    """Redimensionne l'image à MAX_PHOTO_SIDE max, JPEG 85%."""
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((MAX_PHOTO_SIDE, MAX_PHOTO_SIDE * 2), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue()


def _upload_sync(player_id: str, file_data: bytes) -> str:
    """Exécution synchrone de l'upload Supabase — à appeler via asyncio.to_thread."""
    from supabase import create_client

    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    filename = f"{player_id}/{uuid.uuid4()}.jpg"
    try:
        client.storage.from_(BUCKET).upload(
            path=filename,
            file=file_data,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )
    except Exception as exc:
        raise RuntimeError(f"Upload Supabase échoué : {exc}") from exc
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"


def _save_local(player_id: str, file_data: bytes) -> str:
    """Fallback local pour le développement — cross-platform."""
    import tempfile, pathlib

    tmp_dir = pathlib.Path(tempfile.gettempdir()) / "orbyon_photos"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    path = tmp_dir / f"{player_id}.jpg"
    path.write_bytes(file_data)
    return path.as_uri()  # file:///... compatible Windows + Linux


async def upload_player_photo(player_id: str, file_data: bytes, content_type: str) -> str:
    """
    Upload asynchrone de la photo joueur.
    Utilise asyncio.to_thread pour ne pas bloquer la boucle d'événements.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return await asyncio.to_thread(_save_local, player_id, file_data)
    return await asyncio.to_thread(_upload_sync, player_id, file_data)
