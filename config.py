"""
Configuration file for Scientific Truth Machine (STM)
Contains all system settings and parameters
"""

import os

# ============================================================================
# PATHS - Where everything is stored
# ============================================================================

# Base directory (the STM_APP folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
RESULTS_DIR = os.path.join(DATA_DIR, 'results')

# Database path
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DATABASE_DIR, 'stm_database.db')

# ============================================================================
# MODULE 1: PERCEPTION & EXTRACTION SETTINGS
# ============================================================================

# OCR Settings
OCR_LANGUAGE = 'eng'  # English
OCR_CONFIG = '--oem 3 --psm 6'  # Tesseract config

# Visual Analysis Settings
IMAGE_SIZE = (224, 224)  # Image size for VGG-19
VISUAL_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for visual cues

# Nutrition Parser Settings
REQUIRED_NUTRIENTS = ['energy', 'fat', 'saturated_fat', 'sugar', 'salt', 'protein', 'fiber']

# ============================================================================
# MODULE 2: SEMANTIC VALIDATION SETTINGS
# ============================================================================

# EU Register Settings
EU_REGISTER_URL = "https://ec.europa.eu/food/safety/labelling_nutrition/claims/register/public/"

# Scientific Evidence Settings
PUBMED_API_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EVIDENCE_CONFIDENCE_THRESHOLD = 0.7
MAX_EVIDENCE_RESULTS = 10

# Legal Keywords (trigger regulatory check)
HEALTH_CLAIM_KEYWORDS = [
    'reduces', 'prevents', 'treats', 'improves', 'supports', 'maintains',
    'protects', 'strengthens', 'boosts', 'enhances', 'promotes',
    'cardiovascular', 'immune', 'digestive', 'bone', 'cognitive',
    'heart', 'blood pressure', 'cholesterol', 'diabetes', 'weight loss'
]

# ============================================================================
# MODULE 3: NUTRITION ANALYSIS SETTINGS
# ============================================================================

# Anomaly Detection Settings
ANOMALY_CONTAMINATION = 0.1  # Expected proportion of outliers (10%)
N_ESTIMATORS = 100  # Number of trees in Isolation Forest
RANDOM_STATE = 42  # For reproducibility

# Category-specific thresholds (these will be learned from data)
CATEGORY_MIN_SAMPLES = 50  # Minimum products needed to define a category

# ============================================================================
# SCORING SETTINGS (Final Scientific Integrity Score)
# ============================================================================

# Weights for combining different module scores
WEIGHT_SEMANTIC = 0.4  # 40% weight to semantic validation
WEIGHT_LEGAL = 0.3     # 30% weight to legal compliance
WEIGHT_NUTRITION = 0.3  # 30% weight to nutritional consistency

# Integrity Score Thresholds
SCORE_EXCELLENT = 0.85  # 85%+ = Excellent integrity
SCORE_GOOD = 0.70       # 70-85% = Good integrity
SCORE_MODERATE = 0.50   # 50-70% = Moderate concerns
# Below 50% = High risk

# ============================================================================
# SYSTEM SETTINGS
# ============================================================================

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
VERBOSE = True      # Print progress messages

# Performance
BATCH_SIZE = 32
MAX_WORKERS = 4  # Parallel processing threads

# API Rate Limits
API_DELAY = 0.5  # Seconds between API calls (to avoid getting blocked)

print("✅ Configuration loaded successfully!")
print(f"📁 Base directory: {BASE_DIR}")
print(f"💾 Database path: {DB_PATH}")