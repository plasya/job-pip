"""Route job URLs to appropriate fetchers based on domain."""

def route_job_url(url: str) -> str:
    """
    Route a job URL to the appropriate fetcher based on the domain.
    
    Args:
        url: Job posting URL.
    
    Returns:
        String identifier for the ATS platform or "generic".
    """
    url_lower = url.lower()
    
    if "boards.greenhouse.io" in url_lower:
        return "greenhouse"
    elif "jobs.lever.co" in url_lower:
        return "lever"
    elif "myworkdayjobs.com" in url_lower:
        return "workday"
    else:
        return "generic"