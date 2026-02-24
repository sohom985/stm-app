"""
Nutrition Parser Module
Extracts and normalizes nutrition facts from product labels
Finds values like: calories, fat, sugar, protein, etc.
"""

import re
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REQUIRED_NUTRIENTS

class NutritionParser:
    """
    Parses nutrition facts from extracted text
    Converts everything to per-100g basis for fair comparison
    """
    
    def __init__(self):
        """Initialize the nutrition parser"""
        print("🥗 Nutrition Parser initialized!")
        
        # Nutrition keywords to look for (with variations)
        self.nutrient_patterns = {
            'energy_kj': [r'energy.*?(\d+)\s*kj', r'(\d+)\s*kj'],
            'energy_kcal': [r'energy.*?(\d+)\s*kcal', r'(\d+)\s*kcal', r'calories.*?(\d+)'],
            'fat': [r'fat.*?(\d+\.?\d*)\s*g', r'total fat.*?(\d+\.?\d*)'],
            'saturated_fat': [r'saturated.*?(\d+\.?\d*)\s*g', r'saturates.*?(\d+\.?\d*)'],
            'carbohydrates': [r'carbohydrate.*?(\d+\.?\d*)\s*g', r'carbs.*?(\d+\.?\d*)'],
            'sugar': [r'sugar.*?(\d+\.?\d*)\s*g', r'sugars.*?(\d+\.?\d*)'],
            'protein': [r'protein.*?(\d+\.?\d*)\s*g'],
            'salt': [r'salt.*?(\d+\.?\d*)\s*g'],
            'fiber': [r'fiber.*?(\d+\.?\d*)\s*g', r'fibre.*?(\d+\.?\d*)']
        }
        
        print(f"✅ Monitoring {len(self.nutrient_patterns)} nutrients")
    
    def extract_nutrition_from_text(self, text):
        """
        Extract nutrition values from text using pattern matching
        
        Args:
            text: Extracted text from product label
            
        Returns:
            Dictionary with nutrition values
        """
        print("🔍 Searching for nutrition facts in text...")
        
        # Convert to lowercase for easier matching
        text_lower = text.lower()
        
        nutrition_data = {}
        
        # Try to find each nutrient
        for nutrient, patterns in self.nutrient_patterns.items():
            value = None
            
            # Try each pattern until we find a match
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        value = float(match.group(1))
                        break  # Found it! Stop searching
                    except (ValueError, IndexError):
                        continue
            
            nutrition_data[nutrient] = value
        
        # Count how many nutrients we found
        found_count = sum(1 for v in nutrition_data.values() if v is not None)
        print(f"✅ Found {found_count}/{len(self.nutrient_patterns)} nutrients")
        
        return nutrition_data
    
    def detect_serving_size(self, text):
        """
        Detect serving size from text
        Important for converting to per-100g basis
        
        Args:
            text: Extracted text
            
        Returns:
            Serving size in grams (or None if not found)
        """
        text_lower = text.lower()
        
        # Common patterns for serving size
        patterns = [
            r'serving size.*?(\d+)\s*g',
            r'per\s+(\d+)\s*g',
            r'portion.*?(\d+)\s*g'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                serving_size = float(match.group(1))
                print(f"📏 Detected serving size: {serving_size}g")
                return serving_size
        
        print("⚠️  Serving size not detected, assuming per-100g")
        return 100.0  # Default to 100g
    
    def normalize_to_per_100g(self, nutrition_data, serving_size):
        """
        Convert nutrition values to per-100g basis
        This allows fair comparison between products!
        
        Args:
            nutrition_data: Dictionary with nutrition values
            serving_size: Size of serving in grams
            
        Returns:
            Normalized nutrition data (per 100g)
        """
        if serving_size == 100.0:
            print("✅ Already per-100g, no conversion needed")
            return nutrition_data
        
        print(f"🔄 Converting from per-{serving_size}g to per-100g...")
        
        # Calculate multiplication factor
        factor = 100.0 / serving_size
        
        normalized = {}
        for nutrient, value in nutrition_data.items():
            if value is not None:
                normalized[nutrient] = round(value * factor, 2)
            else:
                normalized[nutrient] = None
        
        print(f"✅ Normalized to per-100g (factor: {factor:.2f})")
        return normalized
    
    def validate_nutrition_data(self, nutrition_data):
        """
        Check if nutrition data makes sense
        Catches obvious errors like negative values or impossible ranges
        
        Args:
            nutrition_data: Dictionary with nutrition values
            
        Returns:
            Dictionary with validation results
        """
        print("🔍 Validating nutrition data...")
        
        issues = []
        
        # Check for negative values (impossible!)
        for nutrient, value in nutrition_data.items():
            if value is not None and value < 0:
                issues.append(f"{nutrient} is negative ({value}g) - impossible!")
        
        # Check if fat + carbs + protein > 100g (per 100g) - impossible!
        fat = nutrition_data.get('fat', 0) or 0
        carbs = nutrition_data.get('carbohydrates', 0) or 0
        protein = nutrition_data.get('protein', 0) or 0
        total_macros = fat + carbs + protein
        
        if total_macros > 105:  # Allow 5g margin for error
            issues.append(f"Total macronutrients ({total_macros:.1f}g) exceeds 100g - data error!")
        
        # Check if saturated fat > total fat (impossible!)
        sat_fat = nutrition_data.get('saturated_fat', 0) or 0
        if sat_fat > fat:
            issues.append(f"Saturated fat ({sat_fat}g) > total fat ({fat}g) - impossible!")
        
        # Check if sugar > carbohydrates (impossible!)
        sugar = nutrition_data.get('sugar', 0) or 0
        if sugar > carbs:
            issues.append(f"Sugar ({sugar}g) > carbohydrates ({carbs}g) - impossible!")
        
        if issues:
            print(f"⚠️  Found {len(issues)} validation issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Nutrition data validated successfully!")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
    
    def parse_nutrition_label(self, text):
        """
        Complete nutrition parsing pipeline
        Extract → Normalize → Validate
        
        Args:
            text: Text extracted from product label
            
        Returns:
            Complete nutrition analysis
        """
        print("\n" + "="*50)
        print("🥗 PARSING NUTRITION LABEL")
        print("="*50)
        
        # Step 1: Extract nutrition values
        raw_nutrition = self.extract_nutrition_from_text(text)
        
        # Step 2: Detect serving size
        serving_size = self.detect_serving_size(text)
        
        # Step 3: Normalize to per-100g
        normalized_nutrition = self.normalize_to_per_100g(raw_nutrition, serving_size)
        
        # Step 4: Validate
        validation = self.validate_nutrition_data(normalized_nutrition)
        
        # Step 5: Check completeness
        missing_nutrients = [
            nutrient for nutrient in REQUIRED_NUTRIENTS
            if normalized_nutrition.get(nutrient) is None
        ]
        
        if missing_nutrients:
            print(f"⚠️  Missing {len(missing_nutrients)} required nutrients: {missing_nutrients}")
        else:
            print("✅ All required nutrients found!")
        
        return {
            'nutrition_per_100g': normalized_nutrition,
            'original_serving_size': serving_size,
            'validation': validation,
            'missing_nutrients': missing_nutrients,
            'completeness': len(missing_nutrients) == 0
        }
    
    def create_nutrition_summary(self, nutrition_data):
        """
        Create human-readable summary of nutrition data
        
        Args:
            nutrition_data: Parsed nutrition dictionary
            
        Returns:
            Formatted summary string
        """
        parsed = nutrition_data['nutrition_per_100g']
        
        summary = "\n" + "="*50 + "\n"
        summary += "📊 NUTRITION FACTS (per 100g)\n"
        summary += "="*50 + "\n"
        
        # Energy
        if parsed.get('energy_kcal'):
            summary += f"Energy: {parsed['energy_kcal']} kcal\n"
        
        # Macronutrients
        summary += "\nMACRONUTRIENTS:\n"
        for nutrient in ['fat', 'saturated_fat', 'carbohydrates', 'sugar', 'protein', 'fiber']:
            value = parsed.get(nutrient)
            if value is not None:
                summary += f"  {nutrient.replace('_', ' ').title()}: {value}g\n"
            else:
                summary += f"  {nutrient.replace('_', ' ').title()}: Not found\n"
        
        # Salt
        if parsed.get('salt') is not None:
            summary += f"\nSALT: {parsed['salt']}g\n"
        
        # Validation status
        summary += "\n" + "="*50 + "\n"
        if nutrition_data['validation']['is_valid']:
            summary += "✅ Data validated successfully\n"
        else:
            summary += "⚠️  Validation issues detected\n"
        
        summary += "="*50 + "\n"
        
        return summary


# Test the nutrition parser
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING NUTRITION PARSER")
    print("=" * 60)
    
    parser = NutritionParser()
    
    # Example nutrition label text
    sample_text = """
    NUTRITION FACTS
    Serving size: 50g
    
    Per 50g serving:
    Energy: 200 kcal (850 kJ)
    Fat: 5g
    - Saturated Fat: 2g
    Carbohydrates: 30g
    - Sugar: 15g
    Protein: 8g
    Fiber: 3g
    Salt: 0.5g
    """
    
    print("\n📝 Sample nutrition label:")
    print(sample_text)
    
    # Parse it
    result = parser.parse_nutrition_label(sample_text)
    
    # Show summary
    print(parser.create_nutrition_summary(result))
    
    print("\n✅ Nutrition Parser test complete!")