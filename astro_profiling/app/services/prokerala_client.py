from __future__ import annotations

from prokerala_api import ApiClient  # type: ignore
from app.core.config import PROKERALA_CLIENT_ID, PROKERALA_CLIENT_SECRET


def get_api_client() -> ApiClient:
    # Simple factory in case you later add retries / caching / rotation
    return ApiClient(PROKERALA_CLIENT_ID, PROKERALA_CLIENT_SECRET)
