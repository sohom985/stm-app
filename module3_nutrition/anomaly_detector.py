"""
Anomaly Detector Module
Detects products with suspicious nutritional profiles
Uses Isolation Forest algorithm (unsupervised anomaly detection)
"""

import numpy as np
import pandas as pd
# Removed heavy ML dependencies for Streamlit Cloud deployment
# from sklearn.ensemble import IsolationForest
# from sklearn.preprocessing import StandardScaler
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANOMALY_CONTAMINATION, N_ESTIMATORS, RANDOM_STATE

class NutritionAnomalyDetector:
    """
    Detects nutritional anomalies using statistical analysis
    Think of it as: A detective finding products that don't match their claims!
    """
    
    def __init__(self):
        """Initialize the anomaly detector"""
        print("🔍 Nutrition Anomaly Detector initialized!")
        
        # Model parameters
        self.contamination = ANOMALY_CONTAMINATION
        self.n_estimators = N_ESTIMATORS
        self.random_state = RANDOM_STATE
        
        # The detector model (Isolation Forest) - MOCKED for Streamlit Cloud
        self.model = "MockedModel"
        self.scaler = "MockedScaler"
        
        # Nutrients to monitor
        self.key_nutrients = [
            'energy_kcal', 'fat', 'saturated_fat', 
            'sugar', 'salt', 'protein', 'fiber'
        ]
        
        print(f"✅ Monitoring {len(self.key_nutrients)} key nutrients")
    
    def prepare_nutrition_data(self, nutrition_records):
        """
        Prepare nutrition data for anomaly detection
        
        Args:
            nutrition_records: List of nutrition dictionaries
            
        Returns:
            DataFrame ready for analysis
        """
        print("📊 Preparing nutrition data...")
        
        # Convert to DataFrame
        df = pd.DataFrame(nutrition_records)
        
        # Keep only key nutrients
        available_nutrients = [n for n in self.key_nutrients if n in df.columns]
        df_nutrients = df[available_nutrients].copy()
        
        # Fill missing values with median (statistical approach)
        df_nutrients = df_nutrients.fillna(df_nutrients.median())
        
        print(f"✅ Prepared {len(df_nutrients)} products with {len(available_nutrients)} nutrients")
        
        return df_nutrients
    
    def train_detector(self, nutrition_data):
        """
        Train the anomaly detection model (MOCKED for Streamlit Cloud)
        """
        print("\n🎓 Training anomaly detector (Mocked)...")
        self.model = "TrainedMock"
        return self.model
    
    def detect_anomalies(self, nutrition_data):
        """
        Detect which products are nutritional anomalies (MOCKED for Streamlit Cloud)
        Always returns "normal" for demo purposes to avoid scikit-learn dependency
        """
        print("🔍 Detecting anomalies (Mocked)...")
        
        results = nutrition_data.copy()
        
        # In the mocked version, nothing is an anomaly
        results['is_anomaly'] = False
        results['anomaly_score'] = 1.0
        results['anomaly_score_normalized'] = 1.0
        
        anomaly_count = results['is_anomaly'].sum()
        print(f"✅ Detection complete! Found {anomaly_count} anomalies")
        
        return results
    
    def identify_anomaly_causes(self, product_data, nutrition_data):
        """
        Identify WHICH nutrients make a product anomalous
        This helps explain WHY it's flagged
        
        Args:
            product_data: Single product's nutrition (Series)
            nutrition_data: All products (DataFrame) for comparison
            
        Returns:
            Dictionary explaining the anomaly
        """
        print("🔍 Identifying anomaly causes...")
        
        causes = {}
        
        for nutrient in self.key_nutrients:
            if nutrient not in nutrition_data.columns:
                continue
            
            product_value = product_data.get(nutrient, 0)
            
            # Calculate percentile (where does this product rank?)
            percentile = (nutrition_data[nutrient] < product_value).mean() * 100
            
            # Calculate how many standard deviations from mean
            mean = nutrition_data[nutrient].mean()
            std = nutrition_data[nutrient].std()
            z_score = (product_value - mean) / std if std > 0 else 0
            
            # Flag if extreme (beyond 2 standard deviations)
            is_extreme = abs(z_score) > 2
            
            causes[nutrient] = {
                'value': round(product_value, 2),
                'category_mean': round(mean, 2),
                'percentile': round(percentile, 1),
                'z_score': round(z_score, 2),
                'is_extreme': is_extreme
            }
        
        # Find most extreme nutrients
        extreme_nutrients = [
            (nutrient, data['z_score']) 
            for nutrient, data in causes.items() 
            if data['is_extreme']
        ]
        
        # Sort by absolute z-score (most extreme first)
        extreme_nutrients.sort(key=lambda x: abs(x[1]), reverse=True)
        
        print(f"✅ Found {len(extreme_nutrients)} extreme nutrients")
        
        return {
            'all_nutrients': causes,
            'extreme_nutrients': extreme_nutrients,
            'top_contributor': extreme_nutrients[0][0] if extreme_nutrients else None
        }
    
    def analyze_product_category(self, products_by_category):
        """
        Analyze anomalies within specific product categories
        Example: Compare protein bars to other protein bars (not to candy!)
        
        Args:
            products_by_category: Dictionary mapping category -> list of products
            
        Returns:
            Category-specific anomaly analysis
        """
        print("\n📁 Analyzing products by category...")
        
        all_results = {}
        
        for category, products in products_by_category.items():
            print(f"\n🏷️  Category: {category} ({len(products)} products)")
            
            if len(products) < 5:
                print(f"⚠️  Too few products in '{category}', skipping...")
                continue
            
            # Prepare data
            nutrition_df = self.prepare_nutrition_data(products)
            
            # Train detector for this category
            self.train_detector(nutrition_df)
            
            # Detect anomalies
            results = self.detect_anomalies(nutrition_df)
            
            all_results[category] = results
        
        print(f"\n✅ Analyzed {len(all_results)} categories!")
        
        return all_results
    
    def assess_claim_nutrition_consistency(self, health_claims, nutrition_data):
        """
        Check if nutrition facts support the health claims
        Example: "Low sugar" claim but 20g sugar per 100g = INCONSISTENT!
        
        Args:
            health_claims: List of health claims made
            nutrition_data: Product's nutrition facts
            
        Returns:
            Consistency assessment
        """
        print("\n🔍 Checking claim-nutrition consistency...")
        
        inconsistencies = []
        
        # Define claim-nutrition rules
        rules = {
            'low.*?sugar': {
                'nutrient': 'sugar',
                'threshold': 5.0,
                'comparison': 'less_than',
                'message': 'Low sugar claims require ≤5g per 100g'
            },
            'low.*?fat': {
                'nutrient': 'fat',
                'threshold': 3.0,
                'comparison': 'less_than',
                'message': 'Low fat claims require ≤3g per 100g'
            },
            'high.*?protein': {
                'nutrient': 'protein',
                'threshold': 12.0,
                'comparison': 'greater_than',
                'message': 'High protein claims require ≥12g per 100g (≥20% energy)'
            },
            'high.*?fiber': {
                'nutrient': 'fiber',
                'threshold': 6.0,
                'comparison': 'greater_than',
                'message': 'High fiber claims require ≥6g per 100g'
            },
            'low.*?salt': {
                'nutrient': 'salt',
                'threshold': 0.3,
                'comparison': 'less_than',
                'message': 'Low salt claims require ≤0.3g per 100g'
            }
        }
        
        import re
        
        for claim in health_claims:
            claim_text = claim if isinstance(claim, str) else claim.get('text', '')
            claim_lower = claim_text.lower()
            
            for pattern, rule in rules.items():
                if re.search(pattern, claim_lower):
                    nutrient = rule['nutrient']
                    threshold = rule['threshold']
                    comparison = rule['comparison']
                    
                    actual_value = nutrition_data.get(nutrient, 0)
                    
                    # Check consistency
                    if comparison == 'less_than':
                        is_consistent = actual_value <= threshold
                    else:  # greater_than
                        is_consistent = actual_value >= threshold
                    
                    if not is_consistent:
                        inconsistencies.append({
                            'claim': claim_text,
                            'nutrient': nutrient,
                            'required': f"{'≤' if comparison == 'less_than' else '≥'} {threshold}g",
                            'actual': f"{actual_value}g",
                            'severity': 'high',
                            'message': rule['message']
                        })
        
        if inconsistencies:
            print(f"⚠️  Found {len(inconsistencies)} claim-nutrition inconsistencies!")
        else:
            print("✅ No claim-nutrition inconsistencies detected")
        
        return {
            'is_consistent': len(inconsistencies) == 0,
            'inconsistencies': inconsistencies
        }
    
    def create_anomaly_report(self, product_name, anomaly_result, causes):
        """
        Create human-readable anomaly report
        
        Args:
            product_name: Name of the product
            anomaly_result: Anomaly detection result
            causes: Anomaly cause analysis
            
        Returns:
            Formatted report string
        """
        report = "\n" + "="*60 + "\n"
        report += f"🔍 NUTRITIONAL ANOMALY REPORT: {product_name}\n"
        report += "="*60 + "\n\n"
        
        if anomaly_result['is_anomaly']:
            report += "⚠️  STATUS: ANOMALY DETECTED\n"
            report += f"   Anomaly Score: {anomaly_result['anomaly_score_normalized']:.2f}\n"
            report += "   (0 = most anomalous, 1 = most normal)\n\n"
            
            if causes['extreme_nutrients']:
                report += "🚨 EXTREME NUTRIENTS:\n"
                for nutrient, z_score in causes['extreme_nutrients']:
                    data = causes['all_nutrients'][nutrient]
                    report += f"   {nutrient}: {data['value']}g\n"
                    report += f"     Category average: {data['category_mean']}g\n"
                    report += f"     Percentile: {data['percentile']:.0f}%\n"
                    report += f"     Z-score: {z_score:.2f}\n"
                report += "\n"
        else:
            report += "✅ STATUS: NORMAL (No anomaly detected)\n"
            report += f"   Anomaly Score: {anomaly_result['anomaly_score_normalized']:.2f}\n\n"
        
        report += "="*60 + "\n"
        
        return report


# Test the anomaly detector
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING ANOMALY DETECTOR")
    print("=" * 60)
    
    detector = NutritionAnomalyDetector()
    
    # Create sample data (protein bars with one suspicious outlier)
    sample_products = [
        {'energy_kcal': 350, 'fat': 12, 'saturated_fat': 3, 'sugar': 8, 'salt': 0.5, 'protein': 20, 'fiber': 5},
        {'energy_kcal': 340, 'fat': 11, 'saturated_fat': 2, 'sugar': 9, 'salt': 0.4, 'protein': 21, 'fiber': 6},
        {'energy_kcal': 360, 'fat': 13, 'saturated_fat': 4, 'sugar': 7, 'salt': 0.6, 'protein': 19, 'fiber': 5},
        {'energy_kcal': 355, 'fat': 12, 'saturated_fat': 3, 'sugar': 8, 'salt': 0.5, 'protein': 22, 'fiber': 4},
        {'energy_kcal': 500, 'fat': 25, 'saturated_fat': 15, 'sugar': 35, 'salt': 2.0, 'protein': 5, 'fiber': 1},  # OUTLIER!
        {'energy_kcal': 345, 'fat': 10, 'saturated_fat': 2, 'sugar': 9, 'salt': 0.3, 'protein': 23, 'fiber': 6},
    ]
    
    print("\n📊 Sample data: 6 protein bars (1 suspicious)")
    
    # Prepare data
    nutrition_df = detector.prepare_nutrition_data(sample_products)
    
    # Train detector
    detector.train_detector(nutrition_df)
    
    # Detect anomalies
    results = detector.detect_anomalies(nutrition_df)
    
    print("\n🔍 Results:")
    for idx, row in results.iterrows():
        status = "⚠️  ANOMALY" if row['is_anomaly'] else "✅ Normal"
        print(f"   Product {idx+1}: {status} (score: {row['anomaly_score_normalized']:.2f})")
    
    print("\n✅ Anomaly Detector test complete!")