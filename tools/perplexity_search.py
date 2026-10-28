"""Perplexity API configuration for search."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


def search_perplexity(query: str, model: str = "sonar") -> str:
    """Search using Perplexity API.
    
    Args:
        query: Search query
        model: Perplexity model (default: sonar for online search)
        
    Returns:
        Search results as text
    """
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY not set in .env")
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a startup market research analyst specializing in the Egyptian and MENA startup ecosystem. "
                    "Your task is to search for real, factual information about startups, companies, competitors, and market data. "
                    "Provide specific, verifiable information including: "
                    "- Company names and founding dates "
                    "- Funding rounds and amounts "
                    "- Real competitors in the market "
                    "- Market size and industry data for Egypt/MENA "
                    "- Website URLs and sources when available "
                    "Be concise but thorough. If information is not found, clearly state that. "
                    "Focus on Egyptian and MENA region data when available."
                )
            },
            {
                "role": "user",
                "content": query
            }
        ]
    }
    
    response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    
    result = response.json()
    return result['choices'][0]['message']['content']


def validate_company_exists(company_name: str, industry: str, location: str = "Egypt") -> dict:
    """Check if a company with similar name exists in the market.
    
    Args:
        company_name: Name to search for
        industry: Industry sector
        location: Geographic location (default: Egypt)
        
    Returns:
        Dict with exists (bool), details (str), sources (list)
    """
    query = f'Does a startup or company named "{company_name}" exist in the {industry} industry in {location}? Provide company details if found, including website and any public information.'
    
    result = search_perplexity(query)
    
    # Enhanced heuristic: check for various "not found" patterns
    not_found_phrases = [
        'not found', 
        'no results', 
        'does not exist', 
        'couldn\'t find',
        'could not find',
        'no evidence',
        'there is no',
        'no information',
        'no company',
        'no startup',
        'does not appear'
    ]
    
    result_lower = result.lower()
    exists = not any(phrase in result_lower for phrase in not_found_phrases)
    
    return {
        "exists": exists,
        "details": result,
        "query": query
    }


def get_real_competitors(industry: str, location: str = "Egypt", count: int = 5) -> dict:
    """Get list of real competitors in a specific industry and location.
    
    Args:
        industry: Industry sector (e.g., fintech, healthtech)
        location: Geographic location (default: Egypt)
        count: Number of competitors to find
        
    Returns:
        Dict with competitors list and market context
    """
    query = f'List the top {count} {industry} startups and companies currently operating in {location}. Include company names, what they do, and their funding status if known.'
    
    result = search_perplexity(query)
    
    return {
        "industry": industry,
        "location": location,
        "competitors": result,
        "query": query
    }


def validate_market_size(industry: str, location: str = "Egypt") -> dict:
    """Get market size and opportunity data for an industry in a location.
    
    Args:
        industry: Industry sector
        location: Geographic location (default: Egypt)
        
    Returns:
        Dict with market size info and sources
    """
    query = f'What is the market size and opportunity for {industry} in {location}? Provide TAM/SAM estimates, growth rates, and recent trends if available.'
    
    result = search_perplexity(query)
    
    return {
        "industry": industry,
        "location": location,
        "market_data": result,
        "query": query
    }


def get_common_challenges(industry: str, stage: str, location: str = "Egypt") -> dict:
    """Search for real common challenges faced by startups in specific industry/stage.
    
    Args:
        industry: Industry sector (e.g., fintech, healthtech, edtech)
        stage: Startup stage (e.g., Seed, Series A, Early Growth)
        location: Geographic location (default: Egypt)
        
    Returns:
        Dict with common challenges, real examples, and context
    """
    query = (
        f'What are the most common challenges faced by {stage} stage {industry} startups in {location}? '
        f'Include real examples of challenges like: regulatory issues, customer acquisition costs, '
        f'talent shortages, funding access, market competition, technology barriers, and operational challenges. '
        f'Provide specific examples from actual companies if available.'
    )
    
    result = search_perplexity(query)
    
    return {
        "industry": industry,
        "stage": stage,
        "location": location,
        "challenges": result,
        "query": query
    }


def validate_challenges_for_profile(industry: str, stage: str, proposed_challenges: list, location: str = "Egypt") -> dict:
    """Validate if proposed challenges match real challenges in the market.
    
    Args:
        industry: Industry sector
        stage: Startup stage
        proposed_challenges: List of challenge descriptions from generated profile
        location: Geographic location
        
    Returns:
        Dict with validation results and real-world alignment
    """
    challenges_text = ", ".join(proposed_challenges)
    
    query = (
        f'For {stage} stage {industry} startups in {location}, how realistic are these challenges: {challenges_text}? '
        f'Are these actual problems faced by real companies in this sector? '
        f'Provide context on whether these challenges align with real market conditions.'
    )
    
    result = search_perplexity(query)
    
    return {
        "industry": industry,
        "stage": stage,
        "proposed_challenges": proposed_challenges,
        "validation": result,
        "query": query
    }


if __name__ == '__main__':
    print("="*60)
    print("Testing Perplexity Search Functions")
    print("="*60)
    
    # Test 1: Check if a company exists
    print("\n1. Testing company existence check...")
    result1 = validate_company_exists("funin", "fintech", "Egypt")
    print(f"Exists: {result1['exists']}")
    print(f"Details:\n{result1['details']}\n")
    
    # Test 2: Get real competitors
    print("\n2. Testing competitor search...")
    result2 = get_real_competitors("fintech", "Egypt", 5)
    print(f"Competitors:\n{result2['competitors']}\n")
    
    # Test 3: Validate market size
    print("\n3. Testing market size validation...")
    result3 = validate_market_size("edtech", "Egypt")
    print(f"Market Data:\n{result3['market_data']}\n")
    
    # Test 4: Get common challenges
    print("\n4. Testing common challenges search...")
    result4 = get_common_challenges("fintech", "Seed", "Egypt")
    print(f"Challenges:\n{result4['challenges']}\n")
    
    # Test 5: Validate proposed challenges
    print("\n5. Testing challenge validation...")
    sample_challenges = [
        "Difficulty obtaining Central Bank licenses",
        "High customer acquisition costs",
        "Limited access to venture capital"
    ]
    result5 = validate_challenges_for_profile("fintech", "Seed", sample_challenges, "Egypt")
    print(f"Validation:\n{result5['validation']}\n")
