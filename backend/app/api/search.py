from fastapi import APIRouter, Query
from app.integrations.harvest import harvest_get

router = APIRouter(tags=["search"])


@router.get("/search")
def search_alumni(query: str = Query(..., min_length=1)):
    """Search for alumni by name.
    
    Calls Harvest API to search LinkedIn leads by name.
    
    Args:
        query: Search term (name)
        
    Returns:
        List of matching alumni profiles
    """
    results = harvest_get("/linkedin/lead-search", {"search": query})
    return results


@router.get("/search/profile")
def get_profile(url: str = Query(..., min_length=1)):
    """Fetch a LinkedIn profile by URL.
    
    Calls Harvest API to retrieve detailed profile information.
    
    Args:
        url: LinkedIn profile URL
        
    Returns:
        Profile details including name, title, company, etc.
    """
    profile = harvest_get("/linkedin/profile", {"url": url})
    return profile
