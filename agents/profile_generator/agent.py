"""Profile Generator Agent - Main Implementation."""

import random
import uuid
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.load_stages import get_all_stages, get_stage_data
from agents.profile_generator.config import INDUSTRIES, LOCATIONS, STAGE_MAPPING
from agents.profile_generator.prompts import build_profile_prompt
from tools.llm_config import generate_text
from tools.perplexity_search import (
    validate_company_exists,
    get_real_competitors,
    validate_market_size,
    get_common_challenges,
    validate_challenges_for_profile
)


class ProfileGeneratorAgent:
    """Generates realistic Egyptian startup profiles."""
    
    def __init__(self, enable_validation: bool = True):
        """Initialize the agent.
        
        Args:
            enable_validation: Enable online validation with Perplexity (default: True)
        """
        self.stages = get_all_stages()
        self.enable_validation = enable_validation
        self.validation_results = {}  # Store validation results for review
    
    def generate(self, stage_override: Optional[str] = None, industry_hint: Optional[str] = None) -> Dict[str, Any]:
        """Generate a startup profile.
        
        Args:
            stage_override: Force specific stage
            industry_hint: Prefer specific industry
            
        Returns:
            Complete startup profile matching schema
        """
        # Step 1: Generate skeleton
        skeleton = self._sample_skeleton(stage_override, industry_hint)
        
        # Step 2: Enrich with LLM (with name validation)
        enriched = self._enrich_with_llm(skeleton)
        
        # Step 3: Validate company name doesn't exist
        if self.enable_validation:
            enriched = self._validate_and_regenerate_name(enriched, skeleton)
        
        # Step 4: Build final profile
        profile = self._build_final_profile(skeleton, enriched)
        
        # Step 5: Enrich with online research
        if self.enable_validation:
            profile = self._enrich_with_online_research(profile, skeleton)
        
        return profile
    
    def _sample_skeleton(self, stage_override: Optional[str], industry_hint: Optional[str]) -> Dict[str, Any]:
        """Sample a valid startup skeleton from stage data.
        
        Args:
            stage_override: Force specific stage
            industry_hint: Prefer specific industry
            
        Returns:
            Skeleton with stage, industry, metrics
        """
        # Select stage
        if stage_override:
            stage = stage_override
        else:
            stage = random.choice(self.stages)
        
        # Get stage data
        stage_info = get_stage_data(stage)
        if not stage_info:
            raise ValueError(f"Stage {stage} not found in data")
        
        # Select industry
        if industry_hint and industry_hint in INDUSTRIES:
            industry = industry_hint
        else:
            industry = random.choice(INDUSTRIES)
        
        # Sample metrics based on stage
        skeleton = {
            "profile_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "stage": stage,
            "stage_schema": STAGE_MAPPING.get(stage, stage),
            "industry": industry,
            "location": random.choice(LOCATIONS),
            "revenue_range": stage_info['revenue_range'],
            "funding_range": stage_info['funding_range'],
            "team_composition": stage_info['team_composition'],
            "traits_egypt": stage_info['traits_egypt'],
            "challenges_keywords": stage_info['challenges_keywords'],
            "is_deep_tech": random.random() < 0.15  # 15% are deep tech
        }
        
        return skeleton
    
    def _enrich_with_llm(self, skeleton: Dict[str, Any]) -> Dict[str, Any]:
        """Call LLM to generate narrative content.
        
        Args:
            skeleton: Basic skeleton with metrics
            
        Returns:
            LLM-generated enrichment data
        """
        prompt = build_profile_prompt(skeleton)
        
        # Call LLM
        response_text = generate_text(prompt, model="gemini-2.5-flash-lite")
        
        # Parse JSON response
        # Remove markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            enriched = json.loads(response_text)
            return enriched
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {e}")
            print(f"Response: {response_text[:500]}")
            raise
    
    def _validate_and_regenerate_name(self, enriched: Dict[str, Any], skeleton: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """Validate company name doesn't exist, regenerate if needed.
        
        Args:
            enriched: LLM-generated content with company_name
            skeleton: Basic skeleton for context
            max_retries: Maximum regeneration attempts
            
        Returns:
            Enriched data with validated unique company name
        """
        company_name = enriched['company_name']
        industry = skeleton['industry']
        location = skeleton['location']
        
        print(f"\n[Validation] Checking if '{company_name}' exists in {industry}...")
        
        for attempt in range(max_retries):
            # Check if company exists
            result = validate_company_exists(company_name, industry, location)
            
            if not result['exists']:
                print(f"[Validation] ✓ '{company_name}' is unique and safe to use")
                self.validation_results['company_name_check'] = {
                    "name": company_name,
                    "exists": False,
                    "attempts": attempt + 1
                }
                return enriched
            else:
                print(f"[Validation] ✗ Conflict detected: '{company_name}' already exists")
                print(f"[Validation] Details: {result['details'][:200]}...")
                
                if attempt < max_retries - 1:
                    print(f"[Validation] Regenerating name (attempt {attempt + 2}/{max_retries})...")
                    # Generate new name by calling LLM again (just for name)
                    new_name_prompt = f"""Generate a unique, fictional Egyptian startup name for a {industry} company in {location}.
                    
Requirements:
- Must be completely fictional and not conflict with real companies
- Should sound Egyptian or MENA-relevant
- Can be Arabic transliteration or English
- Format: Just return the company name, nothing else

Example good names: TechNile, SahelPay, ZahraTech, NileSolutions
DO NOT use: {company_name}"""
                    
                    new_name = generate_text(new_name_prompt, model="gemini-2.5-flash-lite").strip()
                    enriched['company_name'] = new_name
                    company_name = new_name
                    print(f"[Validation] New name generated: '{company_name}'")
        
        # Max retries reached
        print(f"[Validation] ⚠ Max retries reached. Using '{company_name}' with conflict flag")
        self.validation_results['company_name_check'] = {
            "name": company_name,
            "exists": True,
            "warning": "Name may conflict with existing company",
            "attempts": max_retries
        }
        return enriched
    
    def _enrich_with_online_research(self, profile: Dict[str, Any], skeleton: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich profile with real market data from online search.
        
        Args:
            profile: Generated profile
            skeleton: Original skeleton with stage/industry
            
        Returns:
            Profile enriched with real market intelligence
        """
        industry = skeleton['industry']
        stage = skeleton['stage']
        location = skeleton['location']
        
        print(f"\n[Research] Gathering market intelligence for {industry} in {location}...")
        
        # Get real competitors
        print(f"[Research] Finding real competitors...")
        competitors_result = get_real_competitors(industry, location, count=5)
        self.validation_results['real_competitors'] = competitors_result
        
        # Validate market size
        print(f"[Research] Validating market size...")
        market_result = validate_market_size(industry, location)
        self.validation_results['market_data'] = market_result
        
        # Get common challenges for this stage/industry
        print(f"[Research] Researching common challenges...")
        challenges_result = get_common_challenges(industry, stage, location)
        self.validation_results['common_challenges'] = challenges_result
        
        # Validate proposed challenges
        proposed_challenges = [profile['startup_profile']['challenges']['primary_challenge']['description']]
        proposed_challenges.extend([c['description'] for c in profile['startup_profile']['challenges']['secondary_challenges']])
        
        print(f"[Research] Validating proposed challenges...")
        validation_result = validate_challenges_for_profile(industry, stage, proposed_challenges, location)
        self.validation_results['challenge_validation'] = validation_result
        
        # Add research data to profile metadata
        profile['startup_profile']['metadata']['web_research_basis'] = [
            {
                "source": "Perplexity Search",
                "competitors_found": competitors_result['competitors'][:300] + "...",  # Truncate for schema
                "market_validation": market_result['market_data'][:300] + "...",
                "challenges_research": challenges_result['challenges'][:300] + "...",
                "validation_summary": validation_result['validation'][:300] + "..."
            }
        ]
        
        print(f"[Research] ✓ Market intelligence gathered successfully\n")
        
        return profile
    
    def _build_final_profile(self, skeleton: Dict[str, Any], enriched: Dict[str, Any]) -> Dict[str, Any]:
        """Combine skeleton and enriched data into final schema-compliant profile.
        
        Args:
            skeleton: Deterministic skeleton
            enriched: LLM-generated content
            
        Returns:
            Complete profile matching startup_profile_schema.json
        """
        profile = {
            "startup_profile": {
                "profile_id": skeleton['profile_id'],
                "generated_at": skeleton['generated_at'],
                "company_overview": {
                    "name": enriched['company_name'],
                    "industry": skeleton['industry'],
                    "founded": enriched['founded'],
                    "location": skeleton['location'],
                    "tagline": enriched['tagline'],
                    "is_deep_tech": skeleton['is_deep_tech']
                },
                "stage_context": {
                    "current_stage": skeleton['stage_schema'],
                    "stage_description": f"Startup is at {skeleton['stage']} stage",
                    "typical_characteristics": skeleton['traits_egypt'],
                    "egypt_context": skeleton['traits_egypt'],
                    "ecosystem_position": f"{skeleton['industry']} startup in Egyptian ecosystem"
                },
                "business_summary": {
                    "revenue": enriched['revenue'],
                    "funding_raised": enriched['funding_raised'],
                    "team_size": enriched['team_size'],
                    "team_composition": skeleton['team_composition'],
                    "active_users": enriched['active_users'],
                    "growth_rate": enriched['growth_rate']
                },
                "product": {
                    "name": enriched['product_name'],
                    "description": enriched['product_description'],
                    "key_features": enriched['key_features'],
                    "technology": enriched['technology'],
                    "stage_of_development": enriched['stage_of_development']
                },
                "market_positioning": {
                    "target_market": enriched['target_market'],
                    "market_size": enriched['market_size'],
                    "competitors": enriched['competitors'],
                    "differentiation": enriched['differentiation']
                },
                "challenges": {
                    "primary_challenge": enriched['primary_challenge'],
                    "secondary_challenges": enriched['secondary_challenges'],
                    "stage_typical_issues": skeleton['challenges_keywords'].split(';')
                },
                "business_narrative": {
                    "elevator_pitch": enriched['elevator_pitch'],
                    "problem_statement": enriched['problem_statement'],
                    "solution_overview": enriched['solution_overview'],
                    "market_opportunity": enriched['market_opportunity'],
                    "traction": enriched['traction'],
                    "swot_analysis": enriched['swot_analysis'],
                    "current_priorities": enriched['current_priorities']
                },
                "metadata": {
                    "stage_data_source": "Data.csv",
                    "web_research_basis": [],
                    "challenge_categories": [enriched['primary_challenge']['type']] + [c['type'] for c in enriched['secondary_challenges']]
                }
            }
        }
        
        return profile


if __name__ == '__main__':
    # Test full profile generation
    agent = ProfileGeneratorAgent()
    profile = agent.generate(stage_override="Seed", industry_hint="fintech")
    
    print("=== Generated Profile ===")
    print(json.dumps(profile, indent=2))
