"""Load and structure Egyptian startup stages data from CSV."""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


# Column indices in the CSV
COLUMNS = {
    'stage': 0,
    'revenue_range': 2,
    'funding_range': 3,
    'traits_egypt': 5,
    'challenges_keywords': 17,
    'team_composition': 14,
    'startup_has': 7,
}


def load_stages_data() -> Dict[str, Dict[str, Any]]:
    """Load and parse startup stages data from CSV.
    
    Returns:
        Dictionary with stage names as keys and stage data as values.
    """
    csv_path = Path(__file__).parent / 'Data.csv'
    stages = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        
        for row in reader:
            if not row or not row[COLUMNS['stage']].strip():
                continue
            
            stage_name = row[COLUMNS['stage']].strip()
            
            stages[stage_name] = {
                'stage': stage_name,
                'revenue_range': row[COLUMNS['revenue_range']].strip(),
                'funding_range': row[COLUMNS['funding_range']].strip(),
                'traits_egypt': row[COLUMNS['traits_egypt']].strip(),
                'challenges_keywords': row[COLUMNS['challenges_keywords']].strip(),
                'team_composition': row[COLUMNS['team_composition']].strip(),
                'startup_has': row[COLUMNS['startup_has']].strip(),
            }
    
    return stages


def get_all_stages() -> List[str]:
    """Get list of all stage names.
    
    Returns:
        List of stage names in order.
    """
    data = load_stages_data()
    return list(data.keys())


def get_stage_data(stage_name: str) -> Optional[Dict[str, Any]]:
    """Get data for a specific stage.
    
    Args:
        stage_name: Name of the stage to retrieve.
    
    Returns:
        Stage data dictionary, or None if stage not found.
    """
    data = load_stages_data()
    return data.get(stage_name)


if __name__ == '__main__':
    # Test: Print data for Seed stage
    print("=== Seed Stage Data ===\n")
    seed_data = get_stage_data('Seed')
    if seed_data:
        for key, value in seed_data.items():
            print(f"{key}: {value}\n")
    
    print("\n=== All Stages ===")
    for stage in get_all_stages():
        print(f"  - {stage}")
