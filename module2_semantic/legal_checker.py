"""
Legal Checker Module
Checks if health claims comply with EU Regulation (EC) No 1924/2006
Ensures claims are legally permitted before products go to market
"""

import re
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import HEALTH_CLAIM_KEYWORDS

class LegalChecker:
    """
    Checks legal compliance of health claims under EU regulations
    Think of it as: Your legal advisor checking if claims are allowed!
    """
    
    def __init__(self):
        """Initialize the legal checker"""
        print("⚖️  Legal Checker initialized!")
        
        # Prohibited claim types (NEVER allowed in EU)
        self.prohibited_claims = {
            'disease_treatment': [
                r'cure.*?(disease|cancer|diabetes|arthritis)',
                r'treat.*?(disease|cancer|diabetes|illness)',
                r'heal.*?(disease|cancer|diabetes)',
                r'reverse.*?(disease|cancer|diabetes)'
            ],
            'weight_loss_rate': [
                r'lose.*?\d+.*?(kg|pounds|lbs).*?(week|month)',
                r'drop.*?\d+.*?(kg|pounds|lbs)',
                r'shed.*?\d+.*?(kg|pounds|lbs)'
            ],
            'medicinal_claims': [
                r'medicine for',
                r'drug for',
                r'pharmaceutical',
                r'prescription'
            ],
            'general_wellness': [
                r'improves.*?general.*?health',
                r'boosts.*?overall.*?wellness',
                r'enhances.*?total.*?well-being'
            ]
        }
        
        # Approved nutrient function claims (simplified list)
        # In real system, this would be loaded from EU Register database
        self.approved_nutrient_claims = {
            'vitamin_c': [
                'contributes to normal function of the immune system',
                'contributes to normal collagen formation',
                'contributes to reduction of tiredness and fatigue'
            ],
            'calcium': [
                'contributes to normal muscle function',
                'needed for maintenance of normal bones',
                'needed for maintenance of normal teeth'
            ],
            'vitamin_d': [
                'contributes to normal absorption of calcium',
                'contributes to maintenance of normal bones',
                'contributes to normal function of immune system'
            ],
            'protein': [
                'contributes to growth in muscle mass',
                'contributes to maintenance of muscle mass',
                'contributes to maintenance of normal bones'
            ],
            'fiber': [
                'contributes to increase in faecal bulk',
                'contributes to maintenance of normal bowel function'
            ]
        }
        
        # Trigger words that require special scrutiny
        self.trigger_words = HEALTH_CLAIM_KEYWORDS
        
        print(f"✅ Loaded {len(self.prohibited_claims)} prohibited claim categories")
        print(f"✅ Loaded {len(self.approved_nutrient_claims)} approved nutrient types")
    
    def detect_prohibited_claims(self, text):
        """
        Detect claims that are NEVER allowed under EU law
        
        Args:
            text: Product text to check
            
        Returns:
            List of prohibited claims found
        """
        print("🔍 Checking for prohibited claims...")
        
        text_lower = text.lower()
        violations = []
        
        for category, patterns in self.prohibited_claims.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    violations.append({
                        'text': match.group(0),
                        'category': category,
                        'severity': 'critical',
                        'reason': f'Claims suggesting {category.replace("_", " ")} are prohibited',
                        'regulation': 'Article 12, Regulation (EC) No 1924/2006'
                    })
        
        if violations:
            print(f"⚠️  Found {len(violations)} PROHIBITED claims!")
        else:
            print("✅ No prohibited claims detected")
        
        return violations
    
    def check_trigger_words(self, text):
        """
        Check for words that trigger health claim regulations
        These words indicate the text is making a health claim
        
        Args:
            text: Product text to check
            
        Returns:
            List of trigger words found
        """
        print("🔍 Checking for regulatory trigger words...")
        
        text_lower = text.lower()
        found_triggers = []
        
        for trigger in self.trigger_words:
            if trigger.lower() in text_lower:
                found_triggers.append(trigger)
        
        if found_triggers:
            print(f"⚠️  Found {len(found_triggers)} trigger words: {found_triggers[:5]}...")
        else:
            print("✅ No trigger words detected")
        
        return found_triggers
    
    def match_to_approved_claims(self, claim_text):
        """
        Check if claim matches an approved EU health claim
        
        Args:
            claim_text: The claim to check
            
        Returns:
            Match result with approval status
        """
        claim_lower = claim_text.lower()
        
        # Check each nutrient's approved claims
        for nutrient, approved_claims in self.approved_nutrient_claims.items():
            for approved_claim in approved_claims:
                # Simple similarity check
                # In real system, this would use semantic similarity (NLP)
                similarity = self._calculate_similarity(claim_lower, approved_claim.lower())
                
                if similarity > 0.7:  # 70% similarity threshold
                    return {
                        'matched': True,
                        'nutrient': nutrient,
                        'approved_wording': approved_claim,
                        'similarity': round(similarity, 2),
                        'status': 'likely_compliant'
                    }
        
        return {
            'matched': False,
            'status': 'not_in_register',
            'recommendation': 'Submit for authorization or remove claim'
        }
    
    def _calculate_similarity(self, text1, text2):
        """
        Simple word-overlap similarity calculation
        Real system would use advanced NLP (BERT, etc.)
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def check_conditions_of_use(self, claim_text, nutrition_data):
        """
        Check if product meets conditions of use for a claim
        Example: "High in Vitamin C" requires ≥30mg per 100g
        
        Args:
            claim_text: The health claim
            nutrition_data: Product's nutrition facts
            
        Returns:
            Conditions check result
        """
        print("🔍 Checking conditions of use...")
        
        # Simplified conditions (real system would have complete database)
        conditions = {
            'high.*?vitamin c': {
                'nutrient': 'vitamin_c',
                'threshold': 30,  # mg per 100g
                'unit': 'mg'
            },
            'source.*?protein': {
                'nutrient': 'protein',
                'threshold': 12,  # % of energy
                'unit': '% energy'
            },
            'high.*?fiber': {
                'nutrient': 'fiber',
                'threshold': 6,  # g per 100g
                'unit': 'g'
            }
        }
        
        claim_lower = claim_text.lower()
        
        for pattern, condition in conditions.items():
            if re.search(pattern, claim_lower):
                # Check if product meets the condition
                # (In this simplified version, we just flag it for manual check)
                return {
                    'condition_applies': True,
                    'required_nutrient': condition['nutrient'],
                    'threshold': condition['threshold'],
                    'unit': condition['unit'],
                    'status': 'needs_verification',
                    'message': f"Product must contain ≥{condition['threshold']}{condition['unit']}"
                }
        
        return {
            'condition_applies': False,
            'status': 'no_specific_conditions'
        }
    
    def assess_legal_risk(self, claim_text, nutrition_data=None):
        """
        Complete legal risk assessment for a claim
        
        Args:
            claim_text: The health claim to assess
            nutrition_data: Optional nutrition facts
            
        Returns:
            Complete legal assessment
        """
        print("\n" + "="*60)
        print(f"⚖️  LEGAL ASSESSMENT: '{claim_text}'")
        print("="*60)
        
        assessment = {
            'claim': claim_text,
            'prohibited': False,
            'violations': [],
            'trigger_words': [],
            'approval_match': {},
            'conditions': {},
            'risk_level': 'unknown'
        }
        
        # Check 1: Prohibited claims
        prohibited = self.detect_prohibited_claims(claim_text)
        if prohibited:
            assessment['prohibited'] = True
            assessment['violations'] = prohibited
            assessment['risk_level'] = 'critical'
            print("🚨 CRITICAL: Contains prohibited claims!")
            return assessment
        
        # Check 2: Trigger words
        triggers = self.check_trigger_words(claim_text)
        assessment['trigger_words'] = triggers
        
        # Check 3: Match to approved claims
        match = self.match_to_approved_claims(claim_text)
        assessment['approval_match'] = match
        
        # Check 4: Conditions of use
        if nutrition_data:
            conditions = self.check_conditions_of_use(claim_text, nutrition_data)
            assessment['conditions'] = conditions
        
        # Determine overall risk level
        if match['matched'] and match['similarity'] > 0.9:
            assessment['risk_level'] = 'low'
            print("✅ LOW RISK: Matches approved claim")
        elif match['matched'] and match['similarity'] > 0.7:
            assessment['risk_level'] = 'moderate'
            print("⚠️  MODERATE RISK: Similar to approved claim but not exact")
        elif triggers:
            assessment['risk_level'] = 'high'
            print("⚠️  HIGH RISK: Contains health claim triggers but not in register")
        else:
            assessment['risk_level'] = 'low'
            print("✅ LOW RISK: No health claim detected")
        
        return assessment
    
    def assess_multiple_claims(self, claims, nutrition_data=None):
        """
        Assess multiple claims at once
        
        Args:
            claims: List of claim dictionaries
            nutrition_data: Optional nutrition facts
            
        Returns:
            Dictionary mapping claims to assessments
        """
        print(f"\n📋 Assessing {len(claims)} claims for legal compliance...")
        
        results = {}
        
        for i, claim in enumerate(claims, 1):
            print(f"\n[{i}/{len(claims)}] Assessing claim...")
            claim_text = claim['text'] if isinstance(claim, dict) else claim
            result = self.assess_legal_risk(claim_text, nutrition_data)
            results[claim_text] = result
        
        print(f"\n✅ All {len(claims)} claims assessed!")
        return results
    
    def create_compliance_report(self, assessment_results):
        """
        Create human-readable compliance report
        
        Args:
            assessment_results: Dictionary of legal assessments
            
        Returns:
            Formatted report string
        """
        report = "\n" + "="*60 + "\n"
        report += "⚖️  LEGAL COMPLIANCE REPORT\n"
        report += "="*60 + "\n\n"
        
        # Count risk levels
        risk_counts = {'critical': 0, 'high': 0, 'moderate': 0, 'low': 0}
        
        for claim_text, assessment in assessment_results.items():
            risk_level = assessment['risk_level']
            risk_counts[risk_level] += 1
            
            report += f"CLAIM: {claim_text}\n"
            report += f"Risk Level: {risk_level.upper()}\n"
            
            if assessment['prohibited']:
                report += "❌ STATUS: PROHIBITED - Remove immediately!\n"
                for violation in assessment['violations']:
                    report += f"  Violation: {violation['reason']}\n"
            elif assessment['approval_match'].get('matched'):
                match = assessment['approval_match']
                report += f"✅ Matches approved claim for {match['nutrient']}\n"
                report += f"  Approved wording: {match['approved_wording']}\n"
                report += f"  Similarity: {match['similarity']:.0%}\n"
            else:
                report += "⚠️  Not found in EU Register\n"
                report += "  Recommendation: Submit for authorization or remove\n"
            
            report += "-" * 60 + "\n\n"
        
        # Summary
        report += "SUMMARY:\n"
        report += f"  Critical Risk: {risk_counts['critical']} claims\n"
        report += f"  High Risk: {risk_counts['high']} claims\n"
        report += f"  Moderate Risk: {risk_counts['moderate']} claims\n"
        report += f"  Low Risk: {risk_counts['low']} claims\n"
        report += "="*60 + "\n"
        
        return report


# Test the legal checker
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING LEGAL CHECKER")
    print("=" * 60)
    
    checker = LegalChecker()
    
    # Sample claims to test
    test_claims = [
        "Supports immune health",  # Should match approved claim
        "Cures cancer",  # PROHIBITED
        "High in Vitamin C",  # Requires conditions check
        "Boosts energy",  # Trigger word but vague
    ]
    
    print("\n📝 Testing claims:")
    for claim in test_claims:
        print(f"  - {claim}")
    
    # Assess claims
    results = checker.assess_multiple_claims(test_claims)
    
    # Show report
    print(checker.create_compliance_report(results))
    
    print("\n✅ Legal Checker test complete!")