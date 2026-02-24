import pandas as pd
import numpy as np
import joblib
import json
from tqdm import tqdm

print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       PRODUCT ANALYSIS WITH TRAINED MODELS               ║
║       Analyze 6,202 Products                             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

# Load models
print("📦 Loading trained models...")
score_model = joblib.load('models/integrity_score_model.pkl')
risk_model = joblib.load('models/risk_classifier_model.pkl')

with open('models/model_config.json', 'r') as f:
    config = json.load(f)

feature_cols = config['feature_cols']
nutrition_features = config['nutrition_features']

print(f"✅ Models loaded (trained on {config['training_samples']:,} samples)\n")

# Load dataset
df = pd.read_csv('data/raw/nutraceuticals_10k_sample.csv')
print(f"📊 Analyzing {len(df):,} products...\n")

# Feature engineering (same as training)
print("🔧 Engineering features...")

df['main_category'] = df['categories'].str.split(',').str[0]

# Category statistics
category_stats = df.groupby('main_category')[nutrition_features].agg(['mean', 'std'])

# Z-scores
for nutrient in nutrition_features:
    df[f'{nutrient}_zscore'] = 0.0
    
    for category in df['main_category'].unique():
        if pd.isna(category):
            continue
        
        mask = df['main_category'] == category
        mean_val = category_stats.loc[category, (nutrient, 'mean')]
        std_val = category_stats.loc[category, (nutrient, 'std')]
        
        if std_val > 0:
            df.loc[mask, f'{nutrient}_zscore'] = (df.loc[mask, nutrient] - mean_val) / std_val

# Ratios
df['protein_to_fat_ratio'] = df['protein'] / (df['fat'] + 1)
df['sugar_to_energy_ratio'] = df['sugar'] / (df['energy_kcal'] + 1)

# Feature matrix
X = df[feature_cols].fillna(0)

# ========================================
# PREDICT
# ========================================
print("🔬 Running predictions...")

df['integrity_score'] = score_model.predict(X)
df['risk_level'] = risk_model.predict(X)

# Clip scores to [0, 1]
df['integrity_score'] = df['integrity_score'].clip(0, 1)

print("✅ Predictions complete!\n")

# ========================================
# SAVE RESULTS
# ========================================
print("💾 Saving results...")

results_df = df[[
    'code', 'name', 'brand', 'categories', 'countries',
    'energy_kcal', 'fat', 'sugar', 'protein', 'salt',
    'integrity_score', 'risk_level'
]]

results_df.to_csv('data/results/stm_analysis_results.csv', index=False)

# Also save with all features for dashboard
df.to_csv('data/processed/analyzed_products_full.csv', index=False)

print(f"✅ Results saved to:")
print(f"   • data/results/stm_analysis_results.csv")
print(f"   • data/processed/analyzed_products_full.csv")

# ========================================
# SUMMARY STATISTICS
# ========================================
print("\n" + "="*70)
print("📊 ANALYSIS SUMMARY")
print("="*70)
print(f"\nAnalyzed: {len(df):,} products")
print(f"\nIntegrity Score Distribution:")
print(f"   Mean: {df['integrity_score'].mean():.1%}")
print(f"   Median: {df['integrity_score'].median():.1%}")
print(f"   Std Dev: {df['integrity_score'].std():.3f}")

print(f"\nRisk Level Distribution:")
print(df['risk_level'].value_counts())

print(f"\nTop 10 Lowest Scoring Products:")
worst = df.nsmallest(10, 'integrity_score')[['name', 'brand', 'integrity_score', 'risk_level']]
print(worst.to_string(index=False))

print(f"\n🎉 Analysis complete! Update dashboard to use real scores!")