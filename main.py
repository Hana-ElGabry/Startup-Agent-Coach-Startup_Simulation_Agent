"""Main entry point for Startup Profile Generator."""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from agents.profile_generator.agent import ProfileGeneratorAgent


def flatten_profile_for_csv(profile: dict) -> dict:
    """Flatten nested profile structure for CSV export.
    
    Args:
        profile: Complete profile dictionary
        
    Returns:
        Flat dictionary suitable for CSV
    """
    p = profile['startup_profile']
    
    flat = {
        'profile_id': p['profile_id'],
        'generated_at': p['generated_at'],
        'company_name': p['company_overview']['name'],
        'industry': p['company_overview']['industry'],
        'founded': p['company_overview']['founded'],
        'location': p['company_overview']['location'],
        'tagline': p['company_overview']['tagline'],
        'is_deep_tech': p['company_overview']['is_deep_tech'],
        'stage': p['stage_context']['current_stage'],
        'stage_description': p['stage_context']['stage_description'],
        'revenue': p['business_summary']['revenue'],
        'funding_raised': p['business_summary']['funding_raised'],
        'team_size': p['business_summary']['team_size'],
        'active_users': p['business_summary']['active_users'],
        'growth_rate': p['business_summary']['growth_rate'],
        'product_name': p['product']['name'],
        'product_description': p['product']['description'],
        'technology': p['product']['technology'],
        'stage_of_development': p['product']['stage_of_development'],
        'target_market': p['market_positioning']['target_market'],
        'market_size': p['market_positioning']['market_size'],
        'differentiation': p['market_positioning']['differentiation'],
        'primary_challenge_type': p['challenges']['primary_challenge']['type'],
        'primary_challenge_desc': p['challenges']['primary_challenge']['description'],
        'elevator_pitch': p['business_narrative']['elevator_pitch'],
        'problem_statement': p['business_narrative']['problem_statement'],
        'solution_overview': p['business_narrative']['solution_overview'],
        'traction': p['business_narrative']['traction'],
    }
    
    # Add array fields as joined strings
    flat['key_features'] = '; '.join(p['product']['key_features'])
    flat['competitors'] = '; '.join(p['market_positioning']['competitors'])
    flat['strengths'] = '; '.join(p['business_narrative']['swot_analysis']['strengths'])
    flat['weaknesses'] = '; '.join(p['business_narrative']['swot_analysis']['weaknesses'])
    flat['opportunities'] = '; '.join(p['business_narrative']['swot_analysis']['opportunities'])
    flat['threats'] = '; '.join(p['business_narrative']['swot_analysis']['threats'])
    flat['current_priorities'] = '; '.join(p['business_narrative']['current_priorities'])
    
    return flat


def save_profile_to_csv(profile: dict, output_dir: Path):
    """Save a single profile to its own CSV file (vertical format).
    
    Args:
        profile: Complete profile dictionary
        output_dir: Directory to save CSV files
    """
    output_dir.mkdir(exist_ok=True)
    
    flat = flatten_profile_for_csv(profile)
    company_name = flat['company_name'].replace(' ', '_').replace('/', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{company_name}_{timestamp}.csv"
    filepath = output_dir / filename
    
    # Write CSV in vertical format (field, value)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Field', 'Value'])
        for field, value in flat.items():
            writer.writerow([field, value])
    
    print(f"✓ Saved: {filepath}")


def generate_profiles(count: int, stage: str = None, industry: str = None, enable_validation: bool = True):
    """Generate multiple startup profiles and save to CSV.
    
    Args:
        count: Number of profiles to generate
        stage: Optional stage filter
        industry: Optional industry filter
        enable_validation: Enable online validation (default: True)
    """
    agent = ProfileGeneratorAgent(enable_validation=enable_validation)
    output_dir = Path('generated_profiles')
    
    print(f"\n{'='*60}")
    print(f"Generating {count} startup profile(s)...")
    if stage:
        print(f"Stage filter: {stage}")
    if industry:
        print(f"Industry filter: {industry}")
    print(f"Validation: {'ENABLED' if enable_validation else 'DISABLED'}")
    print(f"{'='*60}\n")
    
    for i in range(count):
        print(f"[{i+1}/{count}] Generating profile...")
        
        try:
            profile = agent.generate(stage_override=stage, industry_hint=industry)
            save_profile_to_csv(profile, output_dir)
            
            # Print summary
            p = profile['startup_profile']
            print(f"  Company: {p['company_overview']['name']}")
            print(f"  Industry: {p['company_overview']['industry']}")
            print(f"  Stage: {p['stage_context']['current_stage']}")
            print()
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"✓ Generated {count} profile(s) in {output_dir}/")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Usage: python main.py [count] [stage] [industry]")
            print("Example: python main.py 5 Seed fintech")
            sys.exit(1)
    else:
        count = 3  # Default: generate 3 profiles
    
    stage = sys.argv[2] if len(sys.argv) > 2 else None
    industry = sys.argv[3] if len(sys.argv) > 3 else None
    
    generate_profiles(count, stage, industry)
