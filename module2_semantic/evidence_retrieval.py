"""
Evidence Retrieval Module
Retrieves scientific evidence from FREE databases
Uses PubMed (biomedical), and can be extended to other sources
"""

import requests
import time
import os
import sys
from xml.etree import ElementTree

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PUBMED_API_BASE, MAX_EVIDENCE_RESULTS, API_DELAY

class EvidenceRetriever:
    """
    Retrieves scientific evidence from public databases
    Think of it as: A research assistant finding scientific papers!
    """
    
    def __init__(self):
        """Initialize the evidence retriever"""
        print("📚 Evidence Retriever initialized!")
        self.pubmed_base = PUBMED_API_BASE
        self.max_results = MAX_EVIDENCE_RESULTS
        
        # Evidence quality indicators
        self.quality_keywords = {
            'high': ['randomized controlled trial', 'meta-analysis', 'systematic review'],
            'medium': ['cohort study', 'clinical trial', 'prospective study'],
            'low': ['case report', 'in vitro', 'animal study']
        }
        
        print("✅ Ready to retrieve evidence!")
    
    def build_search_query(self, ingredient, health_effect):
        """
        Build optimized search query for scientific databases
        
        Args:
            ingredient: The ingredient to search for (e.g., "vitamin C")
            health_effect: The claimed effect (e.g., "immune support")
            
        Returns:
            Optimized search query
        """
        # Combine ingredient and effect
        query = f"{ingredient} AND {health_effect}"
        
        # Add filters for human studies (more relevant than animal studies)
        query += " AND (human OR clinical)"
        
        print(f"🔍 Built query: '{query}'")
        return query
    
    def search_evidence(self, query, max_results=None):
        """
        Search for scientific evidence
        
        Args:
            query: Search query
            max_results: Maximum results to retrieve
            
        Returns:
            List of evidence items
        """
        if max_results is None:
            max_results = self.max_results
        
        print(f"\n🔍 Searching for evidence: '{query}'")
        print(f"   Searching PubMed (30+ million articles)...")
        
        try:
            # Search PubMed
            search_url = f"{self.pubmed_base}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance'  # Most relevant first
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            time.sleep(API_DELAY)
            
            if response.status_code == 200:
                data = response.json()
                id_list = data.get('esearchresult', {}).get('idlist', [])
                total_count = data.get('esearchresult', {}).get('count', '0')
                
                print(f"✅ Found {total_count} total articles")
                print(f"   Retrieving top {len(id_list)} articles...")
                
                return self._fetch_full_details(id_list)
            else:
                print(f"❌ Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return []
    
    def _fetch_full_details(self, pmid_list):
        """
        Fetch full article details from PubMed
        
        Args:
            pmid_list: List of PubMed IDs
            
        Returns:
            List of detailed article information
        """
        if not pmid_list:
            return []
        
        print(f"📥 Fetching details for {len(pmid_list)} articles...")
        
        try:
            fetch_url = f"{self.pubmed_base}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(pmid_list),
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=params, timeout=20)
            time.sleep(API_DELAY)
            
            if response.status_code == 200:
                return self._parse_pubmed_xml(response.content)
            else:
                print(f"❌ Fetch failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching details: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_content):
        """
        Parse PubMed XML response into structured data
        
        Args:
            xml_content: XML response from PubMed
            
        Returns:
            List of parsed articles
        """
        try:
            root = ElementTree.fromstring(xml_content)
            articles = []
            
            for article_elem in root.findall('.//PubmedArticle'):
                try:
                    # Extract article components
                    title_elem = article_elem.find('.//ArticleTitle')
                    abstract_elem = article_elem.find('.//AbstractText')
                    
                    # Publication date
                    year_elem = article_elem.find('.//PubDate/Year')
                    month_elem = article_elem.find('.//PubDate/Month')
                    
                    # Journal info
                    journal_elem = article_elem.find('.//Journal/Title')
                    
                    # PMID
                    pmid_elem = article_elem.find('.//PMID')
                    
                    # Build article object
                    article = {
                        'pmid': pmid_elem.text if pmid_elem is not None else 'Unknown',
                        'title': title_elem.text if title_elem is not None else 'No title',
                        'abstract': abstract_elem.text if abstract_elem is not None else 'No abstract available',
                        'year': year_elem.text if year_elem is not None else 'Unknown',
                        'month': month_elem.text if month_elem is not None else '',
                        'journal': journal_elem.text if journal_elem is not None else 'Unknown journal'
                    }
                    
                    # Assess evidence quality
                    article['quality'] = self._assess_study_quality(article)
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"⚠️  Error parsing article: {e}")
                    continue
            
            print(f"✅ Successfully parsed {len(articles)} articles")
            return articles
            
        except Exception as e:
            print(f"❌ Error parsing XML: {e}")
            return []
    
    def _assess_study_quality(self, article):
        """
        Assess the quality of scientific evidence
        Based on study type keywords in title/abstract
        
        Args:
            article: Article dictionary
            
        Returns:
            Quality rating (high/medium/low)
        """
        text = (article['title'] + ' ' + article['abstract']).lower()
        
        # Check for high-quality study types
        for keyword in self.quality_keywords['high']:
            if keyword in text:
                return 'high'
        
        # Check for medium-quality study types
        for keyword in self.quality_keywords['medium']:
            if keyword in text:
                return 'medium'
        
        # Default to low if no quality indicators found
        return 'low'
    
    def retrieve_for_claim(self, ingredient, health_effect, max_results=None):
        """
        Retrieve evidence for a specific ingredient-effect claim
        
        Args:
            ingredient: The ingredient (e.g., "omega-3")
            health_effect: The claimed effect (e.g., "heart health")
            max_results: Maximum results to retrieve
            
        Returns:
            Evidence package with articles and summary
        """
        print("\n" + "="*60)
        print(f"📚 RETRIEVING EVIDENCE")
        print(f"   Ingredient: {ingredient}")
        print(f"   Effect: {health_effect}")
        print("="*60)
        
        # Build optimized query
        query = self.build_search_query(ingredient, health_effect)
        
        # Search for evidence
        articles = self.search_evidence(query, max_results)
        
        # Summarize evidence
        summary = self._summarize_evidence(articles)
        
        return {
            'ingredient': ingredient,
            'health_effect': health_effect,
            'query_used': query,
            'articles': articles,
            'summary': summary
        }
    
    def _summarize_evidence(self, articles):
        """
        Create summary of retrieved evidence
        
        Args:
            articles: List of articles
            
        Returns:
            Evidence summary
        """
        if not articles:
            return {
                'total_articles': 0,
                'quality_distribution': {},
                'recent_articles': 0,
                'overall_strength': 'insufficient'
            }
        
        # Count by quality
        quality_counts = {'high': 0, 'medium': 0, 'low': 0}
        for article in articles:
            quality = article.get('quality', 'low')
            quality_counts[quality] += 1
        
        # Count recent articles (last 5 years)
        current_year = 2026
        recent_count = sum(
            1 for article in articles 
            if article.get('year', '0').isdigit() and int(article['year']) >= current_year - 5
        )
        
        # Determine overall strength
        if quality_counts['high'] >= 3:
            strength = 'strong'
        elif quality_counts['high'] >= 1 or quality_counts['medium'] >= 5:
            strength = 'moderate'
        elif len(articles) >= 5:
            strength = 'weak'
        else:
            strength = 'insufficient'
        
        print(f"\n📊 Evidence Summary:")
        print(f"   Total articles: {len(articles)}")
        print(f"   High quality: {quality_counts['high']}")
        print(f"   Medium quality: {quality_counts['medium']}")
        print(f"   Low quality: {quality_counts['low']}")
        print(f"   Recent (5 years): {recent_count}")
        print(f"   Overall strength: {strength.upper()}")
        
        return {
            'total_articles': len(articles),
            'quality_distribution': quality_counts,
            'recent_articles': recent_count,
            'overall_strength': strength,
            'top_3_articles': articles[:3]  # Most relevant
        }
    
    def create_evidence_report(self, evidence_package):
        """
        Create human-readable evidence report
        
        Args:
            evidence_package: Evidence retrieval results
            
        Returns:
            Formatted report string
        """
        report = "\n" + "="*60 + "\n"
        report += "📚 SCIENTIFIC EVIDENCE REPORT\n"
        report += "="*60 + "\n\n"
        
        report += f"CLAIM: {evidence_package['ingredient']} for {evidence_package['health_effect']}\n\n"
        
        summary = evidence_package['summary']
        
        report += "EVIDENCE SUMMARY:\n"
        report += f"  Total Studies: {summary['total_articles']}\n"
        report += f"  High Quality: {summary['quality_distribution']['high']}\n"
        report += f"  Medium Quality: {summary['quality_distribution']['medium']}\n"
        report += f"  Low Quality: {summary['quality_distribution']['low']}\n"
        report += f"  Recent Studies (5y): {summary['recent_articles']}\n"
        report += f"  Overall Strength: {summary['overall_strength'].upper()}\n\n"
        
        report += "TOP SUPPORTING STUDIES:\n"
        report += "-" * 60 + "\n"
        
        for i, article in enumerate(summary['top_3_articles'], 1):
            report += f"{i}. {article['title']}\n"
            report += f"   Journal: {article['journal']}, {article['year']}\n"
            report += f"   Quality: {article['quality'].upper()}\n"
            report += f"   PMID: {article['pmid']}\n"
            report += "-" * 60 + "\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report


# Test the evidence retriever
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING EVIDENCE RETRIEVER")
    print("=" * 60)
    
    retriever = EvidenceRetriever()
    
    print("\n💡 Example: Retrieve evidence for 'Vitamin C and immune support'")
    print("   (Requires internet connection!)")
    
    # Example usage:
    # evidence = retriever.retrieve_for_claim("vitamin c", "immune function", max_results=5)
    # print(retriever.create_evidence_report(evidence))
    
    print("\n✅ Evidence Retriever is ready!")
    print("📝 To use it, run:")
    print("   evidence = retriever.retrieve_for_claim('vitamin c', 'immune support')")
    print("   print(retriever.create_evidence_report(evidence))")