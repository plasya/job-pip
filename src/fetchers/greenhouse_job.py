"""Fetch and parse Greenhouse job postings."""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional


def fetch_greenhouse_job(url: str) -> Dict[str, Optional[str]]:
    """
    Fetch and parse a Greenhouse job posting.
    
    Args:
        url: Greenhouse job URL.
    
    Returns:
        Dictionary with extracted job information.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract job title
        title_elem = soup.find('h1', class_='app-title')
        title = title_elem.get_text(strip=True) if title_elem else None
        
        # Extract company name
        company_elem = soup.find('span', class_='company-name')
        if not company_elem:
            # Try alternative selectors
            company_elem = soup.find('div', class_='company-name')
        company = company_elem.get_text(strip=True) if company_elem else None
        
        # Extract location
        location_elem = soup.find('div', class_='location')
        if not location_elem:
            # Try alternative selectors
            location_elem = soup.find('span', class_='location')
        location = location_elem.get_text(strip=True) if location_elem else None
        
        # Extract job description
        desc_elem = soup.find('div', class_='job-description')
        if not desc_elem:
            # Try alternative selectors
            desc_elem = soup.find('div', id='job-description')
        description_text = desc_elem.get_text(strip=True) if desc_elem else None
        
        return {
            'company': company,
            'title': title,
            'location': location,
            'description_text': description_text
        }
        
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return {
            'company': None,
            'title': None,
            'location': None,
            'description_text': None
        }