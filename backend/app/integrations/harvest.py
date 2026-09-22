import httpx
from fastapi import HTTPException
from app.secretsmanager import get_secret

HARVEST_BASE_URL = "https://api.harvestapi.io"


def _harvest_headers() -> dict:
    """Build headers with API key from secrets."""
    key = get_secret("HARVEST_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="HARVEST_API_KEY not configured")
    return {"X-API-Key": key}


async def harvest_get(path: str, params: dict) -> dict:
    """Async GET request to Harvest API."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{HARVEST_BASE_URL}{path}",
                params=params,
                headers=_harvest_headers()
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Harvest API error: {exc.response.status_code}"
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Harvest API unreachable: {exc.__class__.__name__}"
        )
