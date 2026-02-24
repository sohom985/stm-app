import pandas as pd
import numpy as np
from scipy import stats
import re
from tqdm import tqdm

print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       AUTO-LABELING SYSTEM                               ║
║       Generate Training Data from Rules                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

# Load dataset
df = pd.read_csv('data/raw/nutraceuticals_10k_sample.csv')
print(f"📊 Loaded {len(df):,} products\n")

# ========================================
# LABEL 1: NUTRITION ANOMALIES (Unsupervised)
# ========================================
print("🔍 Generating nutrition anomaly labels...")

from sklearn.ensemble import IsolationForest

# Extract nutrition features
nutrition_cols = ['energy_kcal', 'fat', 'sugar', 'protein', 'salt', 'fiber']
nutrition_data = df[nutrition_cols].fillna(0)

# Train Isolation Forest for EACH category
df['is_nutrition_anomaly'] = False
df['anomaly_score'] = 0.0

for category in tqdm(df['categories'].str.split(',').str[0].unique()):
    if pd.isna(category):
        continue
    
    category_mask = df['categories'].str.contains(category, na=False)
    category_data = nutrition_data[category_mask]
    
    if len(category_data) >= 10:  # Need at least 10 samples
        # Train Isolation Forest
        iso_forest = IsolationForest(contamination=0.15, random_state=42)
        anomaly_labels = iso_forest.fit_predict(category_data)
        anomaly_scores = iso_forest.score_samples(category_data)
        
        # Store labels (1 = normal, -1 = anomaly)
        df.loc[category_mask, 'is_nutrition_anomaly'] = (anomaly_labels == -1)
        df.loc[category_mask, 'anomaly_score'] = anomaly_scores

print(f"✅ Found {df['is_nutrition_anomaly'].sum():,} nutrition anomalies")

# ========================================
# LABEL 2: PROHIBITED CLAIMS (Rule-based)
# ========================================
print("\n⚖️ Generating legal violation labels...")

# EU prohibited claim patterns
prohibited_patterns = [
    # Disease prevention/treatment
    r'prevent[s]?\s+(cancer|diabetes|heart\s+disease|alzheimer)',
    r'cure[s]?\s+(cancer|diabetes|disease)',
    r'treat[s]?\s+(cancer|diabetes|disease)',
    r'fight[s]?\s+(cancer|tumor)',
    r'reduce[s]?\s+risk\s+of\s+(cancer|heart\s+attack|stroke)',
    
    # Prohibited strength claims
    r'strongest',
    r'most\s+powerful',
    r'guaranteed\s+results',
    r'miracle',
    
    # Drug-like claims
    r'clinical[ly]?\s+proven',
    r'doctor\s+recommended',
    r'prescription\s+strength',
]

# Approved claim patterns (general body functions)
approved_patterns = [
    r'support[s]?\s+(immune|health|energy)',
    r'maintain[s]?\s+(health|bone|muscle)',
    r'contribute[s]?\s+to',
    r'high\s+in\s+(protein|vitamin|fiber)',
    r'source\s+of\s+(protein|vitamin|fiber)',
]

def check_claims(text):
    if pd.isna(text):
        return 'unknown', 0.5
    
    text = str(text).lower()
    
    # Check prohibited
    for pattern in prohibited_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return 'prohibited', 0.9
    
    # Check approved
    for pattern in approved_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return 'approved', 0.8
    
    return 'unknown', 0.5

# Apply to product names (in real system, would use full label text)
claim_results = df['name'].apply(check_claims)
df['claim_legality'] = claim_results.apply(lambda x: x[0])
df['claim_confidence'] = claim_results.apply(lambda x: x[1])

print(f"✅ Labeled {(df['claim_legality'] == 'prohibited').sum():,} prohibited claims")
print(f"✅ Labeled {(df['claim_legality'] == 'approved').sum():,} approved claims")

# ========================================
# LABEL 3: CATEGORY-BASED EXPECTATIONS
# ========================================
print("\n📊 Generating category-based labels...")

# Expected nutrition ranges by category
category_expectations = {
    'protein': {
        'protein_min': 15,  # Protein supplements should have >15g protein
        'sugar_max': 5,     # Should be low sugar
    },
    'vitamin': {
        'fat_max': 1,       # Vitamins should be low fat
        'energy_max': 50,   # Low calorie
    },
    'energy-drink': {
        'sugar_min': 5,     # Energy drinks typically high sugar
        'energy_min': 30,
    }
}

df['meets_category_expectations'] = True
df['expectation_violations'] = ''

for idx, row in df.iterrows():
    category = str(row['categories']).lower()
    violations = []
    
    for cat_key, expectations in category_expectations.items():
        if cat_key in category:
            for nutrient, threshold in expectations.items():
                nutrient_name = nutrient.replace('_min', '').replace('_max', '')
                
                if nutrient_name in row and pd.notna(row[nutrient_name]):
                    value = row[nutrient_name]
                    
                    if '_min' in nutrient and value < threshold:
                        violations.append(f"Low {nutrient_name}: {value} < {threshold}")
                    elif '_max' in nutrient and value > threshold:
                        violations.append(f"High {nutrient_name}: {value} > {threshold}")
    
    if violations:
        df.at[idx, 'meets_category_expectations'] = False
        df.at[idx, 'expectation_violations'] = '; '.join(violations)

print(f"✅ Found {(~df['meets_category_expectations']).sum():,} category expectation violations")

# ========================================
# LABEL 4: COMPOSITE INTEGRITY SCORE
# ========================================
print("\n🎯 Computing composite integrity labels...")

# Combine all signals into training label
df['training_label_score'] = 1.0

# Deduct for violations
df.loc[df['is_nutrition_anomaly'], 'training_label_score'] -= 0.2
df.loc[df['claim_legality'] == 'prohibited', 'training_label_score'] -= 0.3
df.loc[~df['meets_category_expectations'], 'training_label_score'] -= 0.15

# Clip to [0, 1]
df['training_label_score'] = df['training_label_score'].clip(0, 1)

# Categorize risk
df['training_label_risk'] = pd.cut(
    df['training_label_score'],
    bins=[0, 0.5, 0.7, 0.85, 1.0],
    labels=['critical', 'high', 'moderate', 'low']
)

print(f"\n📈 Label Distribution:")
print(df['training_label_risk'].value_counts())

# ========================================
# SAVE LABELED DATASET
# ========================================
print("\n💾 Saving labeled dataset...")

labeled_path = 'data/processed/labeled_dataset.csv'
df.to_csv(labeled_path, index=False)

print(f"✅ Saved to: {labeled_path}")

# Summary statistics
print("\n" + "="*70)
print("📊 AUTO-LABELING COMPLETE!")
print("="*70)
print(f"\nLabeled {len(df):,} products with:")
print(f"  • Nutrition anomalies: {df['is_nutrition_anomaly'].sum():,}")
print(f"  • Prohibited claims: {(df['claim_legality'] == 'prohibited').sum():,}")
print(f"  • Category violations: {(~df['meets_category_expectations']).sum():,}")
print(f"\nRisk distribution:")
print(df['training_label_risk'].value_counts())
print(f"\nAverage integrity score: {df['training_label_score'].mean():.1%}")
print("\n🚀 Ready for model training!")