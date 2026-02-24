import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import joblib
import os

print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       CUSTOM MODEL TRAINING                              ║
║       Train STM Models from Scratch                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

# Create models directory
os.makedirs('models', exist_ok=True)

# Load labeled data
df = pd.read_csv('data/processed/labeled_dataset.csv')
print(f"📊 Loaded {len(df):,} labeled products\n")

# ========================================
# FEATURE ENGINEERING
# ========================================
print("🔧 Engineering features...")

# Nutrition features
nutrition_features = ['energy_kcal', 'fat', 'saturated_fat', 'sugar', 'protein', 'salt', 'fiber']

# Statistical features per category
df['main_category'] = df['categories'].str.split(',').str[0]

category_stats = df.groupby('main_category')[nutrition_features].agg(['mean', 'std'])

# Z-scores (how far from category mean)
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

# Ratio features
df['protein_to_fat_ratio'] = df['protein'] / (df['fat'] + 1)
df['sugar_to_energy_ratio'] = df['sugar'] / (df['energy_kcal'] + 1)

# Feature matrix
feature_cols = (
    nutrition_features +
    [f'{n}_zscore' for n in nutrition_features] +
    ['protein_to_fat_ratio', 'sugar_to_energy_ratio']
)

X = df[feature_cols].fillna(0)
y_score = df['training_label_score']
y_risk = df['training_label_risk']

print(f"✅ Created {len(feature_cols)} features\n")

# ========================================
# SPLIT DATA
# ========================================
X_train, X_test, y_score_train, y_score_test, y_risk_train, y_risk_test = train_test_split(
    X, y_score, y_risk, test_size=0.2, random_state=42, stratify=y_risk
)

print(f"📊 Train set: {len(X_train):,} | Test set: {len(X_test):,}\n")

# ========================================
# MODEL 1: INTEGRITY SCORE PREDICTOR (Regression)
# ========================================
print("🧠 Training Model 1: Integrity Score Predictor...")

score_model = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    verbose=1
)

score_model.fit(X_train, y_score_train)

# Evaluate
y_pred_score = score_model.predict(X_test)
mse = mean_squared_error(y_score_test, y_pred_score)
r2 = r2_score(y_score_test, y_pred_score)

print(f"\n✅ Score Model Performance:")
print(f"   MSE: {mse:.4f}")
print(f"   R²: {r2:.4f}")
print(f"   RMSE: {np.sqrt(mse):.4f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': score_model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n📊 Top 10 Important Features:")
print(feature_importance.head(10))

# Save model
joblib.dump(score_model, 'models/integrity_score_model.pkl')
print(f"\n💾 Saved to: models/integrity_score_model.pkl")

# ========================================
# MODEL 2: RISK CLASSIFIER (Classification)
# ========================================
print("\n🧠 Training Model 2: Risk Level Classifier...")

risk_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    class_weight='balanced',
    verbose=1
)

risk_model.fit(X_train, y_risk_train)

# Evaluate
y_pred_risk = risk_model.predict(X_test)

print(f"\n✅ Risk Model Performance:")
print(classification_report(y_risk_test, y_pred_risk))

# Save model
joblib.dump(risk_model, 'models/risk_classifier_model.pkl')
print(f"💾 Saved to: models/risk_classifier_model.pkl")

# ========================================
# SAVE FEATURE LIST
# ========================================
import json

model_config = {
    'feature_cols': feature_cols,
    'nutrition_features': nutrition_features,
    'model_version': '1.0',
    'training_date': pd.Timestamp.now().isoformat(),
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'score_model_mse': float(mse),
    'score_model_r2': float(r2)
}

with open('models/model_config.json', 'w') as f:
    json.dump(model_config, f, indent=2)

print(f"💾 Saved config to: models/model_config.json")

# ========================================
# SUMMARY
# ========================================
print("\n" + "="*70)
print("🎉 MODEL TRAINING COMPLETE!")
print("="*70)
print(f"\n✅ Trained 2 custom models:")
print(f"   1. Integrity Score Predictor (R² = {r2:.3f})")
print(f"   2. Risk Level Classifier (Accuracy = {(y_pred_risk == y_risk_test).mean():.1%})")
print(f"\n📁 Models saved to: models/")
print(f"\n🚀 Ready to analyze all products!")