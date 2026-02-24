"""
Claim Validator Module
Validates health claims against scientific evidence
Uses FREE PubMed database (U.S. National Library of Medicine)
"""

import re
import requests
import time
import os
import sys
from xml.etree import ElementTree

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PUBMED_API_BASE, EVIDENCE_CONFIDENCE_THRESHOLD, MAX_EVIDENCE_RESULTS, API_DELAY

class ClaimValidator:
    """
    Validates health claims using scientific literature
    Think of it as: A fact-checker for health statements!
    """
    
    def __init__(self):
        """Initialize the claim validator"""
        print("🔬 Claim Validator initialized!")
        self.pubmed_base = PUBMED_API_BASE
        self.confidence_threshold = EVIDENCE_CONFIDENCE_THRESHOLD
        self.max_results = MAX_EVIDENCE_RESULTS
        
        # Common health claim patterns
        self.claim_patterns = {
            'disease_prevention': [
                r'prevent.*?(disease|cancer|diabetes|heart disease)',
                r'reduce.*?risk.*?(disease|cancer|diabetes)',
                r'protect.*?against.*?(disease|cancer|diabetes)'
            ],
            'body_function': [
                r'support.*?(immune|digestive|cardiovascular|bone|brain)',
                r'improve.*?(immunity|digestion|circulation|memory)',
                r'strengthen.*?(bones|muscles|immune system)'
            ],
            'nutrient_function': [
                r'source of.*?(vitamin|mineral|protein|fiber)',
                r'high in.*?(vitamin|mineral|antioxidants)',
                r'contains.*?(omega|probiotics|antioxidants)'
            ],
            'general_health': [
                r'boost.*?(energy|vitality|wellness)',
                r'enhance.*?(performance|recovery|health)',
                r'promote.*?(health|wellness|vitality)'
            ]
        }
        
        print("✅ Claim patterns loaded!")
    
    def extract_claims(self, text):
        """
        Extract potential health claims from text
        
        Args:
            text: Product text (from labels, webpages, etc.)
            
        Returns:
            List of detected claims with categories
        """
        print("🔍 Extracting health claims from text...")
        
        text_lower = text.lower()
        detected_claims = []
        
        for category, patterns in self.claim_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    claim = {
                        'text': match.group(0),
                        'category': category,
                        'position': match.start(),
                        'is_explicit': True  # Direct statement
                    }
                    detected_claims.append(claim)
        
        # Remove duplicates
        unique_claims = []
        seen_texts = set()
        for claim in detected_claims:
            if claim['text'] not in seen_texts:
                unique_claims.append(claim)
                seen_texts.add(claim['text'])
        
        print(f"✅ Found {len(unique_claims)} unique health claims")
        return unique_claims
    
    def search_pubmed(self, query, max_results=None):
        """
        Search PubMed database for scientific evidence
        PubMed is FREE and has 30+ million scientific articles!
        
        Args:
            query: Search query (health claim to verify)
            max_results: Maximum number of results (default from config)
            
        Returns:
            List of PubMed article IDs
        """
        if max_results is None:
            max_results = self.max_results
        
        print(f"🔍 Searching PubMed for: '{query}'")
        
        try:
            # Build search URL
            search_url = f"{self.pubmed_base}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json'
            }
            
            # Make request
            response = requests.get(search_url, params=params, timeout=10)
            
            # Wait to respect API rate limits (be nice to free services!)
            time.sleep(API_DELAY)
            
            if response.status_code == 200:
                data = response.json()
                id_list = data.get('esearchresult', {}).get('idlist', [])
                count = data.get('esearchresult', {}).get('count', '0')
                
                print(f"✅ Found {count} articles, retrieved {len(id_list)} IDs")
                return id_list
            else:
                print(f"⚠️  PubMed search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching PubMed: {e}")
            return []
    
    def fetch_article_details(self, pmid_list):
        """
        Fetch article details from PubMed
        
        Args:
            pmid_list: List of PubMed IDs
            
        Returns:
            List of article summaries
        """
        if not pmid_list:
            return []
        
        print(f"📚 Fetching details for {len(pmid_list)} articles...")
        
        try:
            # Build fetch URL
            fetch_url = f"{self.pubmed_base}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(pmid_list),
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=params, timeout=15)
            time.sleep(API_DELAY)
            
            if response.status_code == 200:
                # Parse XML response
                root = ElementTree.fromstring(response.content)
                articles = []
                
                for article in root.findall('.//PubmedArticle'):
                    try:
                        # Extract article info
                        title_elem = article.find('.//ArticleTitle')
                        abstract_elem = article.find('.//AbstractText')
                        year_elem = article.find('.//PubDate/Year')
                        
                        title = title_elem.text if title_elem is not None else 'No title'
                        abstract = abstract_elem.text if abstract_elem is not None else 'No abstract'
                        year = year_elem.text if year_elem is not None else 'Unknown'
                        
                        articles.append({
                            'title': title,
                            'abstract': abstract,
                            'year': year
                        })
                    except Exception as e:
                        print(f"⚠️  Error parsing article: {e}")
                        continue
                
                print(f"✅ Retrieved {len(articles)} article details")
                return articles
            else:
                print(f"⚠️  Failed to fetch articles: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching article details: {e}")
            return []
    
    def analyze_evidence(self, claim_text, articles):
        """
        Analyze scientific evidence for a claim
        
        Args:
            claim_text: The health claim to verify
            articles: List of scientific articles
            
        Returns:
            Evidence analysis with confidence score
        """
        print(f"🔬 Analyzing evidence for: '{claim_text}'")
        
        if not articles:
            return {
                'claim': claim_text,
                'evidence_found': False,
                'confidence': 0.0,
                'supporting_articles': 0,
                'verdict': 'insufficient_evidence'
            }
        
        # Simple evidence scoring
        # In a real system, this would use NLP to understand if articles support/contradict the claim
        # For now, we check if claim keywords appear in articles
        
        claim_keywords = set(claim_text.lower().split())
        supporting_count = 0
        
        for article in articles:
            article_text = (article['title'] + ' ' + article['abstract']).lower()
            
            # Count keyword matches
            matches = sum(1 for keyword in claim_keywords if keyword in article_text)
            
            # If more than 50% of keywords match, consider it supporting
            if matches / len(claim_keywords) > 0.5:
                supporting_count += 1
        
        # Calculate confidence
        confidence = min(supporting_count / len(articles), 1.0)
        
        # Determine verdict
        if confidence >= 0.7:
            verdict = 'well_supported'
        elif confidence >= 0.4:
            verdict = 'moderately_supported'
        elif confidence >= 0.2:
            verdict = 'weakly_supported'
        else:
            verdict = 'insufficient_evidence'
        
        print(f"✅ Evidence analysis complete!")
        print(f"   Supporting articles: {supporting_count}/{len(articles)}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Verdict: {verdict}")
        
        return {
            'claim': claim_text,
            'evidence_found': True,
            'confidence': round(confidence, 2),
            'supporting_articles': supporting_count,
            'total_articles': len(articles),
            'verdict': verdict,
            'recent_evidence': [a for a in articles[:3]]  # Top 3 most relevant
        }
    
    def validate_claim(self, claim_text):
        """
        Complete validation pipeline for a single claim
        Search → Fetch → Analyze
        
        Args:
            claim_text: Health claim to validate
            
        Returns:
            Validation result with evidence
        """
        print("\n" + "="*60)
        print(f"🔬 VALIDATING CLAIM: '{claim_text}'")
        print("="*60)
        
        # Step 1: Search PubMed
        pmid_list = self.search_pubmed(claim_text)
        
        # Step 2: Fetch article details
        articles = self.fetch_article_details(pmid_list)
        
        # Step 3: Analyze evidence
        analysis = self.analyze_evidence(claim_text, articles)
        
        return analysis
    
    def validate_multiple_claims(self, claims):
        """
        Validate multiple claims at once
        
        Args:
            claims: List of claim dictionaries
            
        Returns:
            Dictionary mapping claims to validation results
        """
        print(f"\n📋 Validating {len(claims)} claims...")
        
        results = {}
        
        for i, claim in enumerate(claims, 1):
            print(f"\n[{i}/{len(claims)}] Validating claim...")
            claim_text = claim['text']
            result = self.validate_claim(claim_text)
            results[claim_text] = result
            
            # Add category info
            result['category'] = claim['category']
        
        print(f"\n✅ All {len(claims)} claims validated!")
        return results
    
    def create_validation_report(self, validation_results):
        """
        Create human-readable validation report
        
        Args:
            validation_results: Dictionary of validation results
            
        Returns:
            Formatted report string
        """
        report = "\n" + "="*60 + "\n"
        report += "📊 CLAIM VALIDATION REPORT\n"
        report += "="*60 + "\n\n"
        
        for claim_text, result in validation_results.items():
            report += f"CLAIM: {claim_text}\n"
            report += f"Category: {result.get('category', 'unknown')}\n"
            report += f"Verdict: {result['verdict'].replace('_', ' ').upper()}\n"
            report += f"Confidence: {result['confidence']:.0%}\n"
            
            if result['evidence_found']:
                report += f"Supporting Evidence: {result['supporting_articles']}/{result['total_articles']} articles\n"
            else:
                report += "Supporting Evidence: None found\n"
            
            report += "-" * 60 + "\n\n"
        
        return report


# Test the claim validator
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING CLAIM VALIDATOR")
    print("=" * 60)
    
    validator = ClaimValidator()
    
    # Sample claims to test
    sample_text = """
    This product supports immune health.
    High in Vitamin C.
    May reduce the risk of heart disease.
    Boosts energy and vitality.
    """
    
    print("\n📝 Sample product text:")
    print(sample_text)
    
    # Extract claims
    claims = validator.extract_claims(sample_text)
    
    print(f"\n✅ Found {len(claims)} claims!")
    for claim in claims:
        print(f"  - {claim['text']} ({claim['category']})")
    
    # Note: To validate claims, you need internet connection!
    print("\n💡 To validate claims against PubMed, run:")
    print("   results = validator.validate_multiple_claims(claims)")
    print("   print(validator.create_validation_report(results))")