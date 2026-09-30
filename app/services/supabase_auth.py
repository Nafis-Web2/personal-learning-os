import os

import httpx
from fastapi import HTTPException


def verify_supabase_token(token: str) -> dict:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")

    key = (
        os.getenv("SUPABASE_ANON_KEY", "")
        or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    )

    if not url or not key:
        raise HTTPException(
            503,
            "Authentication is not configured",
        )

    try:
        r = httpx.get(
            f"{url}/auth/v1/user",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {token}",
            },
            timeout=8.0,
        )
    except httpx.HTTPError:
        raise HTTPException(
            503,
            "Authentication service unavailable",
        )

    if r.status_code != 200:
        raise HTTPException(
            401,
            "Invalid or expired session",
        )

    data = r.json()

    owner = os.getenv("OWNER_EMAIL", "").strip().lower()
    email = (data.get("email") or "").strip().lower()

    if owner and email != owner:
        raise HTTPException(
            403,
            "This Learning OS is private",
        )

    return data