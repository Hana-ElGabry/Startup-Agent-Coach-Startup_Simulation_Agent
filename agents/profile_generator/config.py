"""Configuration for Profile Generator Agent."""

# Industries in Egyptian ecosystem
INDUSTRIES = [
    "fintech",
    "healthtech",
    "agritech",
    "edtech",
    "proptech",
    "logistics",
    "e-commerce",
    "saas"
]

# Egyptian cities
LOCATIONS = [
    "Cairo",
    "Giza",
    "Alexandria",
    "New Cairo",
    "6th of October City"
]

# Stage mapping from CSV to schema format
STAGE_MAPPING = {
    "Ideation / Pre-Seed": "Ideation/Pre-Seed",
    "Seed": "Seed",
    "Series A (Early Growth)": "Series A",
    "Series B+ (Growth/Scaling)": "Series B+",
    "Mature / Exit": "Mature/Exit"
}
