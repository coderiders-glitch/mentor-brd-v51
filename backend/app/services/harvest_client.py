import httpx
from fastapi import HTTPException
from typing import List, Dict, Any
from app.secretsmanager import get_secret

HARVEST_BASE_URL = "https://api.harvestapi.io"


def _harvest_headers() -> dict:
    key = get_secret("HARVEST_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="HARVEST_API_KEY not configured")
    return {"X-API-Key": key}


def search_linkedin_leads(search_query: str) -> List[Dict[str, Any]]:
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(
                f"{HARVEST_BASE_URL}/linkedin/lead-search",
                params={"search": search_query},
                headers=_harvest_headers()
            )
            resp.raise_for_status()
            data = resp.json()
            elements = data.get("elements", [])
            results = []
            for element in elements:
                results.append({
                    "name": element.get("name", ""),
                    "title": element.get("title"),
                    "url": element.get("url", "")
                })
            return results
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Harvest API error: {exc.response.status_code}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Harvest API unreachable: {exc.__class__.__name__}")


def get_linkedin_profile(linkedin_url: str) -> Dict[str, Any]:
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(
                f"{HARVEST_BASE_URL}/linkedin/profile",
                params={"url": linkedin_url},
                headers=_harvest_headers()
            )
            resp.raise_for_status()
            data = resp.json()
            element = data.get("element", {})
            return {
                "name": element.get("name"),
                "title": element.get("title"),
                "location": element.get("location"),
                "summary": element.get("summary"),
                "experience": element.get("experience", []),
                "education": element.get("education", [])
            }
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Harvest API error: {exc.response.status_code}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Harvest API unreachable: {exc.__class__.__name__}")