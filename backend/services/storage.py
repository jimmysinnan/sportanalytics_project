from __future__ import annotations
import os, io, uuid
from PIL import Image

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "orbyon-photos")
MAX_PHOTO_SIDE = 800


def resize_photo(data: bytes) -> bytes:
    """Redimensionne l'image à MAX_PHOTO_SIDE max, conserve le ratio."""
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((MAX_PHOTO_SIDE, MAX_PHOTO_SIDE * 2), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue()


async def upload_player_photo(player_id: str, file_data: bytes, content_type: str) -> str:
    """
    Upload photo vers Supabase Storage.
    Fallback local si Supabase non configuré (dev).
    Retourne l'URL publique.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        path = f"/tmp/orbyon_photos/{player_id}.jpg"
        os.makedirs("/tmp/orbyon_photos", exist_ok=True)
        with open(path, "wb") as f:
            f.write(file_data)
        return f"file://{path}"

    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    filename = f"{player_id}/{uuid.uuid4()}.jpg"
    client.storage.from_(BUCKET).upload(
        path=filename,
        file=file_data,
        file_options={"content-type": "image/jpeg", "upsert": "true"},
    )
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
