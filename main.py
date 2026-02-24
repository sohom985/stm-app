"""
MAIN.PY - Scientific Truth Machine (STM)
The master controller that runs the entire verification system

This is the file you run to analyze products!
"""

import os
import sys
from datetime import datetime

# Import our modules
from module1_perception.ocr_extractor import OCRExtractor
from module1_perception.visual_analyzer import VisualAnalyzer
from module1_perception.nutrition_parser import NutritionParser

from module2_semantic.claim_validator import ClaimValidator
from module2_semantic.legal_checker import LegalChecker
from module2_semantic.evidence_retrieval import EvidenceRetriever

from module3_nutrition.anomaly_detector import NutritionAnomalyDetector
from module3_nutrition.category_comparison import CategoryComparison

from database.unified_db import UnifiedDatabase
from config import *

class ScientificTruthMachine:
    """
    The complete STM system
    Analyzes product marketing for scientific truth and legal compliance
    
    Think of this as: The conductor of an orchestra - coordinates all modules!
    """
    
    def __init__(self):
        """Initialize all modules"""
        print("\n" + "="*70)
        print("🔬 SCIENTIFIC TRUTH MACHINE (STM) - INITIALIZING")
        print("="*70 + "\n")
        
        # Initialize database
        print("📦 Connecting to database...")
        self.db = UnifiedDatabase()
        
        # Initialize Module 1 (Perception)
        print("\n Initializing Module 1: Perception & Extraction...")
        self.ocr = OCRExtractor()
        self.visual = VisualAnalyzer()
        self.nutrition_parser = NutritionParser()
        
        # Initialize Module 2 (Semantic)
        print("\n Initializing Module 2: Semantic Validation...")
        self.claim_validator = ClaimValidator()
        self.legal_checker = LegalChecker()
        self.evidence_retriever = EvidenceRetriever()
        
        # Initialize Module 3 (Nutrition)
        print("\n Initializing Module 3: Nutrition Analysis...")
        self.anomaly_detector = NutritionAnomalyDetector()
        self.category_comparison = CategoryComparison()
        
        print("\n" + "="*70)
        print("STM FULLY INITIALIZED - READY TO ANALYZE!")
        print("="*70 + "\n")
    
    def analyze_product(self, product_data):
        """
        Complete analysis pipeline for a single product
        
        Args:
            product_data: Dictionary containing:
                - name: Product name
                - category: Product category
                - brand: Brand name (optional)
                - image_path: Path to product image
                - webpage_path: Path to product webpage (optional)
                
        Returns:
            Complete analysis results with Scientific Integrity Score
        """
        print("\n" + "🔬"*35)
        print(f"ANALYZING: {product_data['name']}")
        print(""*35 + "\n")
        
        # Step 1: Add product to database
        product_id = self.db.add_product(
            product_name=product_data['name'],
            category=product_data.get('category'),
            brand=product_data.get('brand'),
            image_path=product_data.get('image_path'),
            webpage_path=product_data.get('webpage_path')
        )
        
        # ==================================================================
        # MODULE 1: PERCEPTION & EXTRACTION
        # ==================================================================
        print("\n" + "="*70)
        print("MODULE 1: PERCEPTION & EXTRACTION")
        print("="*70)
        
        # 1A: Extract text from image
        print("\n Step 1A: OCR Text Extraction...")
        if product_data.get('image_path') and os.path.exists(product_data['image_path']):
            ocr_result = self.ocr.extract_text(product_data['image_path'])
            extracted_text = ocr_result['raw_text']
        else:
            print("⚠️  No image provided, skipping OCR")
            extracted_text = product_data.get('text', '')
        
        # 1B: Analyze visual cues
        print("\n Step 1B: Visual Analysis...")
        if product_data.get('image_path') and os.path.exists(product_data['image_path']):
            visual_analysis = self.visual.analyze_image_composition(product_data['image_path'])
        else:
            print("⚠️  No image provided, skipping visual analysis")
            visual_analysis = {'health_signals': []}
        
        # 1C: Parse nutrition facts
        print("\n Step 1C: Nutrition Parsing...")
        if extracted_text:
            nutrition_result = self.nutrition_parser.parse_nutrition_label(extracted_text)
            nutrition_data = nutrition_result['nutrition_per_100g']
            
            # Save to database
            self.db.save_nutrition(product_id, nutrition_data)
        else:
            print("⚠️  No text to parse, using provided nutrition data")
            nutrition_data = product_data.get('nutrition', {})
        
        # ==================================================================
        # MODULE 2: SEMANTIC VALIDATION
        # ==================================================================
        print("\n" + "="*70)
        print("MODULE 2: SEMANTIC VALIDATION")
        print("="*70)
        
        # 2A: Extract and validate health claims
        print("\n🔬 Step 2A: Claim Extraction & Validation...")
        claims = self.claim_validator.extract_claims(extracted_text)
        
        # 2B: Legal compliance check
        print("\n Step 2B: Legal Compliance Check...")
        legal_results = self.legal_checker.assess_multiple_claims(claims, nutrition_data)
        
        # 2C: Calculate semantic scores
        semantic_score = self._calculate_semantic_score(legal_results)
        legal_score = self._calculate_legal_score(legal_results)
        
        # ==================================================================
        # MODULE 3: NUTRITION ANALYSIS
        # ==================================================================
        print("\n" + "="*70)
        print("MODULE 3: NUTRITION ANALYSIS")
        print("="*70)
        
        # 3A: Check claim-nutrition consistency
        print("\n Step 3A: Claim-Nutrition Consistency...")
        consistency_check = self.anomaly_detector.assess_claim_nutrition_consistency(
            claims, nutrition_data
        )
        
        # 3B: Calculate nutrition score
        nutrition_score = self._calculate_nutrition_score(
            consistency_check,
            nutrition_data
        )
        
        # ==================================================================
        # FINAL INTEGRATION: SCIENTIFIC INTEGRITY SCORE
        # ==================================================================
        print("\n" + "="*70)
        print("CALCULATING SCIENTIFIC INTEGRITY SCORE")
        print("="*70)
        
        final_score = self._calculate_final_score(
            semantic_score,
            legal_score,
            nutrition_score
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(final_score)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            final_score,
            risk_level,
            legal_results,
            consistency_check
        )
        
        # Save final scores to database
        self.db.save_integrity_score(
            product_id,
            semantic_score,
            legal_score,
            nutrition_score,
            final_score,
            risk_level,
            recommendation
        )
        
        # ==================================================================
        # RETURN COMPLETE ANALYSIS
        # ==================================================================
        
        results = {
            'product_id': product_id,
            'product_name': product_data['name'],
            'timestamp': datetime.now().isoformat(),
            
            # Module 1 results
            'extracted_text': extracted_text,
            'visual_signals': visual_analysis.get('health_signals', []),
            'nutrition': nutrition_data,
            
            # Module 2 results
            'claims': claims,
            'legal_assessment': legal_results,
            
            # Module 3 results
            'consistency_check': consistency_check,
            
            # Final scores
            'scores': {
                'semantic': semantic_score,
                'legal': legal_score,
                'nutrition': nutrition_score,
                'final': final_score
            },
            'risk_level': risk_level,
            'recommendation': recommendation
        }
        
        # Print final report
        self._print_final_report(results)
        
        return results
    
    def _calculate_semantic_score(self, legal_results):
        """Calculate semantic validation score (0-1)"""
        if not legal_results:
            return 1.0  # No claims = no risk
        
        total_claims = len(legal_results)
        good_claims = sum(
            1 for result in legal_results.values()
            if result.get('approval_match', {}).get('matched', False)
        )
        
        return good_claims / total_claims if total_claims > 0 else 1.0
    
    def _calculate_legal_score(self, legal_results):
        """Calculate legal compliance score (0-1)"""
        if not legal_results:
            return 1.0  # No claims = compliant
        
        total_claims = len(legal_results)
        critical_violations = sum(
            1 for result in legal_results.values()
            if result.get('prohibited', False)
        )
        
        high_risk = sum(
            1 for result in legal_results.values()
            if result.get('risk_level') == 'high'
        )
        
        # Critical violations = automatic 0
        if critical_violations > 0:
            return 0.0
        
        # High risk = reduced score
        penalty = (high_risk / total_claims) * 0.5
        
        return max(0.0, 1.0 - penalty)
    
    def _calculate_nutrition_score(self, consistency_check, nutrition_data):
        """Calculate nutrition consistency score (0-1)"""
        # If inconsistent, penalize
        if not consistency_check.get('is_consistent', True):
            num_issues = len(consistency_check.get('inconsistencies', []))
            return max(0.0, 1.0 - (num_issues * 0.3))
        
        return 1.0
    
    def _calculate_final_score(self, semantic_score, legal_score, nutrition_score):
        """Calculate weighted final Scientific Integrity Score"""
        final = (
            WEIGHT_SEMANTIC * semantic_score +
            WEIGHT_LEGAL * legal_score +
            WEIGHT_NUTRITION * nutrition_score
        )
        
        return round(final, 3)
    
    def _determine_risk_level(self, final_score):
        """Determine risk level from final score"""
        if final_score >= SCORE_EXCELLENT:
            return 'low'
        elif final_score >= SCORE_GOOD:
            return 'moderate'
        elif final_score >= SCORE_MODERATE:
            return 'high'
        else:
            return 'critical'
    
    def _generate_recommendation(self, final_score, risk_level, legal_results, consistency_check):
        """Generate actionable recommendation"""
        if risk_level == 'low':
            return "Product appears compliant. Review approved for market entry."
        elif risk_level == 'moderate':
            return "Minor issues detected. Review claims wording and ensure exact match to EU Register."
        elif risk_level == 'high':
            issues = []
            
            # Check for legal issues
            prohibited = sum(1 for r in legal_results.values() if r.get('prohibited'))
            if prohibited > 0:
                issues.append(f"Remove {prohibited} prohibited claim(s)")
            
            # Check for consistency issues
            if not consistency_check.get('is_consistent', True):
                issues.append("Adjust nutrition facts or remove inconsistent claims")
            
            return "Significant compliance risks. Actions required: " + "; ".join(issues)
        else:
            return "CRITICAL: Do NOT place on market. Contains prohibited claims or severe violations."
    
    def _print_final_report(self, results):
        """Print beautiful final report"""
        print("\n" + ""*35)
        print("FINAL SCIENTIFIC INTEGRITY REPORT")
        print(""*35 + "\n")
        
        print(f"Product: {results['product_name']}")
        print(f"Analyzed: {results['timestamp']}")
        print(f"\n{'='*70}\n")
        
        # Scores
        scores = results['scores']
        print(" SCORES:")
        print(f"   Semantic Validation:  {scores['semantic']:.1%}")
        print(f"   Legal Compliance:     {scores['legal']:.1%}")
        print(f"   Nutrition Consistency: {scores['nutrition']:.1%}")
        print(f"\n   {'─'*50}")
        print(f"   FINAL INTEGRITY SCORE: {scores['final']:.1%}")
        print(f"   {'─'*50}\n")
        
        # Risk level
        risk = results['risk_level']
        risk_emoji = {
            'low': '✅',
            'moderate': '⚠️',
            'high': '🚨',
            'critical': '🛑'
        }
        
        print(f"{risk_emoji[risk]} RISK LEVEL: {risk.upper()}")
        print(f"\n RECOMMENDATION:")
        print(f"   {results['recommendation']}")
        
        print(f"\n{'='*70}\n")
        
        # Claims summary
        if results['claims']:
            print(f" DETECTED CLAIMS: {len(results['claims'])}")
            for claim in results['claims'][:3]:
                print(f"   • {claim['text']}")
            if len(results['claims']) > 3:
                print(f"   ... and {len(results['claims'])-3} more")
        
        print("\n" + ""*35 + "\n")
    
    def analyze_multiple_products(self, products_list):
        """Analyze multiple products at once"""
        print(f"\n Analyzing {len(products_list)} products...\n")
        
        results = []
        
        for i, product_data in enumerate(products_list, 1):
            print(f"\n{'='*70}")
            print(f"PRODUCT {i}/{len(products_list)}")
            print(f"{'='*70}\n")
            
            result = self.analyze_product(product_data)
            results.append(result)
        
        return results
    
    def close(self):
        """Cleanup and close database connection"""
        self.db.close()
        print("\n STM session closed")


# ==================================================================
# MAIN EXECUTION
# ==================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║          SCIENTIFIC TRUTH MACHINE (STM)                       ║
    ║          Master Thesis Implementation                         ║
    ║          Sohom Chatterjee - MBA                              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize STM
    stm = ScientificTruthMachine()
    
    # Example: Analyze a sample product
    print("\n💡 STM is ready to analyze products!")
    print("\n📝 To analyze a product, use:")
    print("""
    sample_product = {
        'name': 'Vitamin C 1000mg',
        'category': 'supplements',
        'brand': 'HealthCo',
        'image_path': 'data/raw/product_label.jpg',
        'text': 'Supports immune health. High in Vitamin C.',
        'nutrition': {
            'energy_kcal': 15,
            'fat': 0,
            'saturated_fat': 0,
            'sugar': 3,
            'salt': 0.1,
            'protein': 0,
            'fiber': 0
        }
    }
    
    result = stm.analyze_product(sample_product)
    """)
    
    print("\n STM initialized and ready!")
    
    # Close when done
    # stm.close()