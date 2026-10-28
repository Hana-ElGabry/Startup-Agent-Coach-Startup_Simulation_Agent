"""Prompts for Profile Generator Agent."""


def build_profile_prompt(skeleton: dict) -> str:
    """Build LLM prompt to enrich startup profile.
    
    Args:
        skeleton: Dictionary with stage, industry, metrics from CSV
        
    Returns:
        Formatted prompt string
    """
    
    prompt = f"""You are generating a realistic Egyptian startup profile for a business consulting simulation platform.

HARD CONSTRAINTS - DO NOT VIOLATE:
- Stage: {skeleton['stage']}
- Industry: {skeleton['industry']}
- Location: {skeleton['location']}
- Revenue Range: {skeleton['revenue_range']}
- Funding Range: {skeleton['funding_range']}
- Team: {skeleton['team_composition']}
- Deep Tech: {skeleton['is_deep_tech']}

EGYPTIAN CONTEXT:
{skeleton['traits_egypt']}

TYPICAL CHALLENGES AT THIS STAGE:
{skeleton['challenges_keywords']}

GENERATE A COMPLETE STARTUP PROFILE WITH THESE SECTIONS:

1. COMPANY NAME: Creative but realistic Egyptian startup name (avoid generic Silicon Valley names)

2. TAGLINE: One compelling sentence (max 15 words)

3. FOUNDED: Pick a realistic founding date in format YYYY-MM (must align with stage - Ideation within last 12 months, Seed within last 2 years, etc.)

4. PRODUCT NAME: Name of the main product/service

5. PRODUCT DESCRIPTION: 2-3 sentences explaining what the product does

6. KEY FEATURES: List 3-5 core features (comma-separated)

7. TECHNOLOGY STACK: Brief tech stack summary (e.g., "React Native app with Node.js backend, PostgreSQL")

8. STAGE OF DEVELOPMENT: One of [Idea, MVP, Beta, Production, Mature] - must match the business stage

9. PROBLEM STATEMENT: 1 paragraph describing the problem being solved (mention Egyptian market specifics)

10. SOLUTION OVERVIEW: 1 paragraph explaining how the startup solves it

11. TARGET MARKET: Specific segment (e.g., "SMEs in Cairo and Alexandria" not "Egyptian businesses")

12. MARKET SIZE: Estimate in TAM/SAM/SOM format (e.g., "TAM: 50M potential users in Egypt, SAM: 5M digitally active SMEs")

13. COMPETITORS: List 3-5 real or realistic Egyptian/MENA competitors (comma-separated)

14. DIFFERENTIATION: 1-2 sentences on competitive advantage

15. ELEVATOR PITCH: 2-3 sentences summarizing the business

16. MARKET OPPORTUNITY: 1 paragraph on why now and why Egypt

17. TRACTION: 1 paragraph on current progress/validation (must match stage - early stages = pilots/users, later = revenue/scale)

18. REVENUE: Specific number within the range (e.g., if range is $100K-$500K, pick something like "$250K annual recurring revenue")

19. FUNDING RAISED: Specific number within the range (e.g., if range is $1M-$5M, pick "$2.3M from local VCs")

20. TEAM SIZE: Specific number matching team composition (e.g., if "Technical + Commercial Cofounders + team" then 4-8 people)

21. ACTIVE USERS: Realistic metric for stage (e.g., Seed = "1,500 active users", Series A = "25K+ users")

22. GROWTH RATE: Realistic growth for stage (e.g., early stages = "30% MoM", later = "15% YoY")

23. PRIMARY CHALLENGE: Select ONE main challenge from the typical challenges list, give it a type (e.g., "Market", "Financial", "Technical", "Regulatory", "Operations") and 1-2 sentence description

24. SECONDARY CHALLENGES: Select 2-3 additional challenges from the list, each with type and brief description

25. SWOT ANALYSIS:
    - Strengths: 4-6 items
    - Weaknesses: 4-6 items  
    - Opportunities: 4-6 items
    - Threats: 4-6 items

26. CURRENT PRIORITIES: 3-5 strategic priorities for the next 6-12 months

OUTPUT FORMAT:
Return valid JSON with this structure:
{{
  "company_name": "...",
  "tagline": "...",
  "founded": "YYYY-MM",
  "product_name": "...",
  "product_description": "...",
  "key_features": ["feature1", "feature2", "feature3"],
  "technology": "...",
  "stage_of_development": "...",
  "problem_statement": "...",
  "solution_overview": "...",
  "target_market": "...",
  "market_size": "...",
  "competitors": ["comp1", "comp2", "comp3"],
  "differentiation": "...",
  "elevator_pitch": "...",
  "market_opportunity": "...",
  "traction": "...",
  "revenue": "...",
  "funding_raised": "...",
  "team_size": 5,
  "active_users": "...",
  "growth_rate": "...",
  "primary_challenge": {{
    "type": "...",
    "description": "..."
  }},
  "secondary_challenges": [
    {{"type": "...", "description": "..."}},
    {{"type": "...", "description": "..."}}
  ],
  "swot_analysis": {{
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "opportunities": ["...", "..."],
    "threats": ["...", "..."]
  }},
  "current_priorities": ["...", "...", "..."]
}}

CRITICAL RULES:
- Use Egyptian context (EGP currency, local city names, regional competitors)
- Be specific with numbers - no ranges in output
- Challenges must feel real and consulting-addressable (not fatal flaws)
- Keep consistent with stage (early stages = validation focus, later = scale focus)
- No buzzwords or Silicon Valley clichés
- Return ONLY valid JSON, no markdown formatting
"""
    
    return prompt
