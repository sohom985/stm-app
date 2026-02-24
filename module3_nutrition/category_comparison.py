"""
Category Comparison Module
Compares products within their categories
Ensures fair comparison: protein bars vs protein bars, NOT vs candy!
"""

import numpy as np
import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CATEGORY_MIN_SAMPLES

class CategoryComparison:
    """
    Compares nutrition facts within product categories
    Think of it as: Making sure we compare apples to apples!
    """
    
    def __init__(self):
        """Initialize the category comparison"""
        print("📊 Category Comparison initialized!")
        self.min_samples = CATEGORY_MIN_SAMPLES
        
        # Nutrient benchmarks by category (simplified examples)
        # Real system would learn these from data
        self.category_benchmarks = {
            'protein_bars': {
                'protein': {'min': 15, 'ideal': 20},
                'sugar': {'max': 10, 'ideal': 5},
                'fiber': {'min': 3, 'ideal': 5}
            },
            'breakfast_cereals': {
                'sugar': {'max': 15, 'ideal': 8},
                'fiber': {'min': 3, 'ideal': 6},
                'salt': {'max': 0.8, 'ideal': 0.5}
            },
            'yogurt': {
                'protein': {'min': 3, 'ideal': 6},
                'sugar': {'max': 10, 'ideal': 5},
                'fat': {'max': 5, 'ideal': 2}
            }
        }
        
        print("✅ Category comparison ready!")
    
    def group_by_category(self, products):
        """
        Group products by their category
        
        Args:
            products: List of product dictionaries (must have 'category' field)
            
        Returns:
            Dictionary mapping category -> list of products
        """
        print("📁 Grouping products by category...")
        
        categories = {}
        
        for product in products:
            category = product.get('category', 'uncategorized')
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(product)
        
        # Filter out categories with too few products
        valid_categories = {
            cat: prods for cat, prods in categories.items()
            if len(prods) >= self.min_samples
        }
        
        print(f"✅ Found {len(categories)} categories")
        print(f"   {len(valid_categories)} have enough samples (≥{self.min_samples})")
        
        return valid_categories
    
    def calculate_category_statistics(self, products, nutrients):
        """
        Calculate statistics for a category
        
        Args:
            products: List of products in this category
            nutrients: List of nutrient names to analyze
            
        Returns:
            Dictionary with statistics for each nutrient
        """
        # Convert to DataFrame for easy statistics
        nutrition_data = []
        for product in products:
            nutrition_data.append(product.get('nutrition', {}))
        
        df = pd.DataFrame(nutrition_data)
        
        stats = {}
        
        for nutrient in nutrients:
            if nutrient not in df.columns:
                continue
            
            values = df[nutrient].dropna()
            
            if len(values) == 0:
                continue
            
            stats[nutrient] = {
                'mean': float(values.mean()),
                'median': float(values.median()),
                'std': float(values.std()),
                'min': float(values.min()),
                'max': float(values.max()),
                'q25': float(values.quantile(0.25)),  # 25th percentile
                'q75': float(values.quantile(0.75))   # 75th percentile
            }
        
        return stats
    
    def compare_product_to_category(self, product_nutrition, category_stats):
        """
        Compare a single product to its category statistics
        
        Args:
            product_nutrition: Product's nutrition facts
            category_stats: Category statistics
            
        Returns:
            Comparison results
        """
        print("🔍 Comparing product to category...")
        
        comparison = {}
        
        for nutrient, stats in category_stats.items():
            product_value = product_nutrition.get(nutrient, 0)
            
            # Calculate percentile ranking
            # Where does this product rank in its category?
            mean = stats['mean']
            std = stats['std']
            
            # Z-score: how many standard deviations from mean?
            z_score = (product_value - mean) / std if std > 0 else 0
            
            # Approximate percentile from z-score
            # (using normal distribution approximation)
            from scipy import stats as scipy_stats
            percentile = scipy_stats.norm.cdf(z_score) * 100
            
            # Determine if value is good/bad for this nutrient
            # (For nutrients like sugar/salt: lower is better)
            # (For nutrients like protein/fiber: higher is better)
            
            good_nutrients = ['protein', 'fiber']
            bad_nutrients = ['sugar', 'saturated_fat', 'salt']
            
            if nutrient in good_nutrients:
                # Higher is better
                if product_value >= stats['q75']:
                    rating = 'excellent'
                elif product_value >= stats['median']:
                    rating = 'good'
                elif product_value >= stats['q25']:
                    rating = 'average'
                else:
                    rating = 'poor'
            elif nutrient in bad_nutrients:
                # Lower is better
                if product_value <= stats['q25']:
                    rating = 'excellent'
                elif product_value <= stats['median']:
                    rating = 'good'
                elif product_value <= stats['q75']:
                    rating = 'average'
                else:
                    rating = 'poor'
            else:
                rating = 'neutral'
            
            comparison[nutrient] = {
                'product_value': round(product_value, 2),
                'category_mean': round(mean, 2),
                'category_median': round(stats['median'], 2),
                'percentile': round(percentile, 1),
                'z_score': round(z_score, 2),
                'rating': rating
            }
        
        print(f"✅ Comparison complete for {len(comparison)} nutrients")
        
        return comparison
    
    def rank_products_in_category(self, products, ranking_criteria):
        """
        Rank products within a category based on criteria
        
        Args:
            products: List of products to rank
            ranking_criteria: Dictionary defining how to rank
                Example: {'protein': 'higher_better', 'sugar': 'lower_better'}
            
        Returns:
            Ranked list of products with scores
        """
        print(f"🏆 Ranking {len(products)} products...")
        
        # Extract nutrition data
        nutrition_data = []
        for i, product in enumerate(products):
            nutrition = product.get('nutrition', {})
            nutrition['_index'] = i  # Keep track of original index
            nutrition['_name'] = product.get('name', f'Product {i+1}')
            nutrition_data.append(nutrition)
        
        df = pd.DataFrame(nutrition_data)
        
        # Calculate score for each product
        scores = []
        
        for idx, row in df.iterrows():
            score = 0
            
            for nutrient, direction in ranking_criteria.items():
                if nutrient not in df.columns:
                    continue
                
                # Normalize values to 0-100 scale
                values = df[nutrient].dropna()
                min_val = values.min()
                max_val = values.max()
                
                if max_val > min_val:
                    normalized = (row[nutrient] - min_val) / (max_val - min_val) * 100
                else:
                    normalized = 50  # All same value
                
                # Adjust score based on direction
                if direction == 'higher_better':
                    score += normalized
                elif direction == 'lower_better':
                    score += (100 - normalized)
            
            scores.append({
                'index': row['_index'],
                'name': row['_name'],
                'score': score / len(ranking_criteria),  # Average
                'nutrition': row.to_dict()
            })
        
        # Sort by score (highest first)
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ Ranking complete!")
        
        return scores
    
    def identify_best_and_worst(self, ranked_products, top_n=3):
        """
        Identify best and worst products in category
        
        Args:
            ranked_products: List of ranked products
            top_n: How many to show
            
        Returns:
            Best and worst products
        """
        best = ranked_products[:top_n]
        worst = ranked_products[-top_n:][::-1]  # Reverse worst so worst is first
        
        return {
            'best': best,
            'worst': worst
        }
    
    def create_comparison_report(self, product_name, category, comparison_results):
        """
        Create human-readable comparison report
        
        Args:
            product_name: Name of the product
            category: Product category
            comparison_results: Comparison analysis
            
        Returns:
            Formatted report string
        """
        report = "\n" + "="*60 + "\n"
        report += f"📊 CATEGORY COMPARISON REPORT\n"
        report += f"Product: {product_name}\n"
        report += f"Category: {category}\n"
        report += "="*60 + "\n\n"
        
        # Group by rating
        excellent = []
        good = []
        average = []
        poor = []
        
        for nutrient, data in comparison_results.items():
            rating = data['rating']
            
            if rating == 'excellent':
                excellent.append((nutrient, data))
            elif rating == 'good':
                good.append((nutrient, data))
            elif rating == 'average':
                average.append((nutrient, data))
            elif rating == 'poor':
                poor.append((nutrient, data))
        
        # Show results by rating
        if excellent:
            report += "✅ EXCELLENT (Top 25% in category):\n"
            for nutrient, data in excellent:
                report += f"   {nutrient}: {data['product_value']}g "
                report += f"(category avg: {data['category_mean']}g)\n"
            report += "\n"
        
        if good:
            report += "👍 GOOD (Above average):\n"
            for nutrient, data in good:
                report += f"   {nutrient}: {data['product_value']}g "
                report += f"(category avg: {data['category_mean']}g)\n"
            report += "\n"
        
        if average:
            report += "😐 AVERAGE:\n"
            for nutrient, data in average:
                report += f"   {nutrient}: {data['product_value']}g "
                report += f"(category avg: {data['category_mean']}g)\n"
            report += "\n"
        
        if poor:
            report += "⚠️  POOR (Bottom 25% in category):\n"
            for nutrient, data in poor:
                report += f"   {nutrient}: {data['product_value']}g "
                report += f"(category avg: {data['category_mean']}g)\n"
            report += "\n"
        
        report += "="*60 + "\n"
        
        return report
    
    def create_ranking_report(self, category, ranked_products):
        """
        Create ranking report for a category
        
        Args:
            category: Category name
            ranked_products: List of ranked products
            
        Returns:
            Formatted report string
        """
        report = "\n" + "="*60 + "\n"
        report += f"🏆 CATEGORY RANKING: {category}\n"
        report += "="*60 + "\n\n"
        
        report += f"Total products: {len(ranked_products)}\n\n"
        
        # Top 5
        report += "🥇 TOP 5 PRODUCTS:\n"
        for i, product in enumerate(ranked_products[:5], 1):
            report += f"{i}. {product['name']}\n"
            report += f"   Score: {product['score']:.1f}/100\n"
        
        report += "\n"
        
        # Bottom 5
        report += "⚠️  BOTTOM 5 PRODUCTS:\n"
        bottom_5 = ranked_products[-5:][::-1]
        for i, product in enumerate(bottom_5, 1):
            rank = len(ranked_products) - i + 1
            report += f"{rank}. {product['name']}\n"
            report += f"   Score: {product['score']:.1f}/100\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report


# Test the category comparison
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING CATEGORY COMPARISON")
    print("=" * 60)
    
    comparator = CategoryComparison()
    
    # Sample products in protein bar category
    sample_products = [
        {
            'name': 'ProteinPro Bar',
            'category': 'protein_bars',
            'nutrition': {'protein': 22, 'sugar': 6, 'fat': 8, 'fiber': 5}
        },
        {
            'name': 'MuscleMax Bar',
            'category': 'protein_bars',
            'nutrition': {'protein': 20, 'sugar': 8, 'fat': 10, 'fiber': 4}
        },
        {
            'name': 'FitEnergy Bar',
            'category': 'protein_bars',
            'nutrition': {'protein': 18, 'sugar': 12, 'fat': 7, 'fiber': 3}
        },
        {
            'name': 'HealthyChoice Bar',
            'category': 'protein_bars',
            'nutrition': {'protein': 15, 'sugar': 15, 'fat': 12, 'fiber': 2}
        },
    ]
    
    print("\n📊 Sample: 4 protein bars")
    
    # Group by category
    categories = comparator.group_by_category(sample_products)
    
    # Calculate category stats
    category = 'protein_bars'
    stats = comparator.calculate_category_statistics(
        categories[category],
        ['protein', 'sugar', 'fat', 'fiber']
    )
    
    print(f"\n📈 Category statistics calculated")
    
    # Compare first product
    product = sample_products[0]
    comparison = comparator.compare_product_to_category(
        product['nutrition'],
        stats
    )
    
    # Show report
    print(comparator.create_comparison_report(
        product['name'],
        category,
        comparison
    ))
    
    print("\n✅ Category Comparison test complete!")