import httpx
from fastapi import HTTPException
from app.secretsmanager import get_secret

HARVEST_BASE_URL = "https://api.harvestapi.io"


def _harvest_headers() -> dict:
    """Build headers with API key from Secrets Manager."""
    key = get_secret("HARVEST_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="HARVEST_API_KEY not configured")
    return {"X-API-Key": key}


def harvest_get(path: str, params: dict) -> dict:
    """Make a GET request to the Harvest API.
    
    Args:
        path: API path (e.g., '/linkedin/lead-search')
        params: Query parameters dict
        
    Returns:
        JSON response as dict
        
    Raises:
        HTTPException: 502 for upstream errors, 500 for config errors
    """
    headers = _harvest_headers()
    url = f"{HARVEST_BASE_URL}{path}"
    
    try:
        with httpx.Client(verify=True, timeout=30.0) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        # Upstream returned 4xx/5xx - surface clean 502, don't leak key
        raise HTTPException(
            status_code=502,
            detail=f"Harvest API error: {exc.response.status_code}"
        )
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Harvest API connection failed: {str(exc)}"
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Harvest API timeout: {str(exc)}"
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Harvest API error: {exc.__class__.__name__}"
        )
