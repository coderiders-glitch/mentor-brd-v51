import httpx
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.secretsmanager import get_secret

router = APIRouter(tags=["search"])

HARVEST_BASE_URL = "https://api.harvestapi.io"


def _harvest_headers() -> dict:
    """Build headers for Harvest API authentication."""
    key = get_secret("HARVEST_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="HARVEST_API_KEY not configured")
    return {"X-API-Key": key}


def harvest_get(path: str, params: dict) -> dict:
    """Make a GET request to the Harvest API with proper error handling."""
    headers = _harvest_headers()
    url = f"{HARVEST_BASE_URL}{path}"
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params, headers=headers)
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


class SearchResult(BaseModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    url: str


class ProfileResult(BaseModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    url: str


@router.get("/search")
async def search_alumni(query: str = Query(..., min_length=1)) -> List[SearchResult]:
    """Search for alumni by name or keywords."""
    results = harvest_get("/linkedin/lead-search", {"search": query})
    
    items = results.get("items", []) if isinstance(results, dict) else results
    
    return [
        SearchResult(
            name=item.get("name", ""),
            title=item.get("title"),
            company=item.get("company"),
            url=item.get("url", "")
        )
        for item in items
    ]


@router.get("/profile")
async def get_profile(url: str = Query(..., min_length=1)) -> ProfileResult:
    """Fetch detailed profile for a specific alumni URL."""
    result = harvest_get("/linkedin/profile", {"url": url})
    
    return ProfileResult(
        name=result.get("name", ""),
        title=result.get("title"),
        company=result.get("company"),
        location=result.get("location"),
        summary=result.get("summary"),
        url=result.get("url", url)
    )
