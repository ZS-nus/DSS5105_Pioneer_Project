import os
import re
from fuzzywuzzy import fuzz
from pathlib import Path
import logging
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)

class ReportAnalyzer:
    def __init__(self):
        self.keywords = {
            'data_security': [
                'data security', 'information protection', 'data privacy',
                'data breach', 'information security', 'data encryption',
                'data protection', 'secure data', 'data confidentiality', 'data integrity'
            ],
            'cybersecurity': [
                'cybersecurity', 'cyber threat', 'cyber attack', 'cyber risk',
                'cyber defense', 'cyber incident', 'cyber vulnerability', 'cyber resilience',
                'cyber protection', 'network security', 'cyber crime', 'malware',
                'ransomware', 'phishing', 'firewall', 'cyber awareness'
            ],
            'customer_privacy': [
                'customer privacy', 'privacy policy', 'privacy protection', 'privacy rights',
                'personal information', 'data subject rights', 'privacy compliance', 
                'privacy notice', 'privacy impact', 'customer consent', 'privacy breach',
                'privacy risk', 'privacy management', 'data collection', 'data processing',
                'data retention', 'privacy training', 'privacy framework', 'GDPR', 'CCPA'
            ],
            'ethical_corruption': [
                'ethical conduct', 'anti-corruption', 'bribery', 'integrity',
                'ethical standards', 'code of ethics', 'ethical behavior', 'corruption prevention',
                'ethical compliance', 'ethical guidelines', 'ethical practices', 'anti-fraud'
            ],
            'age_diversity': [
                'age diversity', 'generational diversity', 'age inclusion', 
                'age representation', 'multigenerational workforce', 
                'age discrimination', 'age distribution', 'age profile',
                'age demographics', 'age balance',
                'by age', 'age group', 'years old', 
                '20-30', '31-50', '51 years',  # Common age brackets
                'age data', 'age statistics'
            ],
            'gender_diversity': [
                'gender diversity', 'gender equality', 'gender balance',
                'gender representation', 'gender parity', 'gender bias',
                'gender distribution', 'gender profile', 'gender demographics',
                'women in leadership', 'female representation',
                'by gender', 'male female', 'gender data',
                'gender statistics', 'gender ratio',
                'female %', 'male %', 'women %'  # Common statistical mentions
            ],
            'board_diversity': [
                'board diversity', 'diverse board', 'board composition', 'inclusive governance',
                'diverse leadership', 'board representation', 'diversity in leadership',
                'board inclusivity', 'diverse perspectives in board', 'board member diversity'
            ],
            'risk_management': [
                'risk',
                'risk management', 'risk assessment', 'risk mitigation', 'risk control',
                'enterprise risk management', 'risk identification', 'risk monitoring',
                'risk strategy', 'risk analysis', 'risk reporting', 'risk governance'
            ]
        }
        # Add patterns for year detection
        self.year_patterns = [
            r'Fiscal Year (\d{4})',  # Matches "Fiscal Year 2023"
            r'FY(\d{2,4})',  # Matches FY23, FY2023
            r'ended\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s*,\s*(\d{4})',  # Matches "ended January 29, 2023"
            r'report\s+accurate\s+approximately\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s*,\s*(\d{4})',  # Matches "report accurate approximately May 10, 2023"
            r'(\d{4})\s+NVIDIA\s+Corporation'  # Matches "2023 NVIDIA Corporation"
        ]
        # Get current year
        self.current_year = datetime.now().year

    def check_keywords(self, content: str, keywords: list, similarity_threshold: int = 60) -> int:
        """Check content for keywords with fuzzy matching"""
        content_lower = content.lower()
        
        # First check for exact matches of multi-word phrases
        for keyword in keywords:
            if len(keyword.split()) > 1:
                if keyword.lower() in content_lower:
                    return 1
        
        # Then check for demographic data patterns
        if 'age_diversity' in str(keywords):
            if re.search(r'\d+(?:\s*-\s*\d+)?\s*(?:years?|age)', content_lower):
                return 1
            if re.search(r'(?:age|years?).*?(?:\d+%|\d+\s*\(.*?\))', content_lower):
                return 1
        
        if 'gender_diversity' in str(keywords):
            if re.search(r'(?:male|female).*?(?:\d+%|\d+\s*\(.*?\))', content_lower):
                return 1
        
        # Finally check for single-word fuzzy matches
        for keyword in keywords:
            if len(keyword.split()) == 1:
                for word in re.findall(r'\b\w+\b', content_lower):
                    similarity = fuzz.ratio(keyword.lower(), word)
                    if similarity >= similarity_threshold:
                        return 1
        return 0

    def find_iso_certificates(self, content: str) -> list:
        """Find ISO certificates in content"""
        iso_pattern = r'ISO\s*\d{4,5}(?::\d{4})?'
        iso_certificates = re.findall(iso_pattern, content)
        return list(set(iso_certificates))

    def detect_report_year(self, content: str) -> int:
        """Detect the report year from content"""
        try:
            found_years = []
            for pattern in self.year_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    for match in matches:
                        try:
                            year = int(match)
                            # Convert 2-digit year to 4-digit
                            if year < 100:
                                year += 2000
                            # Validate year is reasonable and not future year
                            if 2000 <= year <= self.current_year:
                                # Give higher priority to years found in fiscal year mentions
                                if 'fiscal year' in pattern.lower():
                                    found_years.extend([year] * 3)  # Add multiple times to weight it higher
                                else:
                                    found_years.append(year)
                        except ValueError:
                            continue
            
            # Return the most common year, or None if no valid years found
            if found_years:
                return Counter(found_years).most_common(1)[0][0]
            return None

        except Exception as e:
            logger.error(f"Error detecting report year: {str(e)}")
            return None

    def analyze_report(self, txt_path: str) -> dict:
        """Analyze a single report file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                content = file.read()

            results = {}
            # Detect report year
            report_year = self.detect_report_year(content)
            results['report_year'] = report_year

            # Check each category
            for category, category_keywords in self.keywords.items():
                result = self.check_keywords(content, category_keywords)
                results[category] = result

            # Find ISO certificates
            iso_certificates = self.find_iso_certificates(content)
            results['iso_certificates'] = iso_certificates

            return {
                "status": "success",
                "analysis": results
            }

        except Exception as e:
            logger.error(f"Error analyzing report: {str(e)}")
            return {
                "status": "error",
                "message": f"Error analyzing report: {str(e)}"
            }
