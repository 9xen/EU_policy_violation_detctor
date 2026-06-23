"""
EU Policy Fetcher - Fetch policies from EUR-Lex API
"""

import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EUPolicyFetcher:
    """Fetch EU policies from EUR-Lex and other EU databases"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.sparql = SPARQLWrapper(config['eurlex']['sparql_endpoint'])
        self.sparql.setReturnFormat(JSON)
        self.base_url = config['eurlex']['rest_endpoint']
        self.language = config['eurlex']['default_language']
        
    def fetch_policies(self, policy_types: List[str] = None) -> pd.DataFrame:
        """Fetch all policies from EUR-Lex using SPARQL"""
        if policy_types is None:
            policy_types = ['REG', 'DIR', 'DEC']
        
        all_policies = []
        
        for ptype in policy_types:
            logger.info(f"Fetching {ptype} policies...")
            policies = self._fetch_by_type(ptype)
            all_policies.extend(policies)
            time.sleep(1)  # Rate limiting
            
        return pd.DataFrame(all_policies)
    
    def _fetch_by_type(self, resource_type: str) -> List[Dict]:
        """Fetch policies by resource type using SPARQL"""
        
        # SPARQL query for EU legislation
        query = f"""
        PREFIX cdm: <http://publications.europa.eu/ontology/cdm/>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX eurovoc: <http://eurovoc.europa.eu/>
        
        SELECT DISTINCT ?work ?celex ?title ?date ?type ?legal_basis ?directory_code
        WHERE {{
            ?work cdm:work_is_about_concept_eurovoc ?eurovoc .
            ?work dct:date ?date .
            ?work cdm:work_is_natural_expression ?expression .
            ?expression cdm:expression_has_language <http://publications.europa.eu/resource/authority/language/ENG> .
            ?expression cdm:expression_has_title ?title .
            ?work cdm:work_has_resource-type ?resource_type .
            ?resource_type skos:prefLabel ?type .
            FILTER(?type = "{resource_type}"@en)
        }}
        ORDER BY DESC(?date)
        LIMIT 1000
        """
        
        self.sparql.setQuery(query)
        
        try:
            results = self.sparql.query().convert()
            policies = self._parse_results(results)
            return policies
        except Exception as e:
            logger.error(f"Error fetching {resource_type}: {e}")
            return []
    
    def _parse_results(self, results: Dict) -> List[Dict]:
        """Parse SPARQL results into structured data"""
        policies = []
        
        for result in results['results']['bindings']:
            policy = {
                'celex_id': result.get('celex', {}).get('value', ''),
                'title': result.get('title', {}).get('value', ''),
                'date': result.get('date', {}).get('value', ''),
                'type': result.get('type', {}).get('value', ''),
                'legal_basis': result.get('legal_basis', {}).get('value', ''),
                'url': result.get('work', {}).get('value', ''),
                'content': self._fetch_policy_content(result.get('celex', {}).get('value', ''))
            }
            policies.append(policy)
        
        return policies
    
    def _fetch_policy_content(self, celex_id: str) -> str:
        """Fetch the full text of a policy by CELEX ID"""
        if not celex_id:
            return ""
        
        url = f"{self.base_url}/EN/TXT/HTML/?uri=CELEX:{celex_id}"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.text
            return ""
        except Exception as e:
            logger.error(f"Error fetching content for {celex_id}: {e}")
            return ""
    
    def fetch_by_celex(self, celex_id: str) -> Dict:
        """Fetch a single policy by CELEX ID"""
        url = f"{self.base_url}/EN/TXT/HTML/?uri=CELEX:{celex_id}"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return {
                    'celex_id': celex_id,
                    'content': response.text,
                    'url': url,
                    'fetched_at': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching {celex_id}: {e}")
            return None
    
    def fetch_eurovoc_concepts(self) -> List[Dict]:
        """Fetch EuroVoc concepts (EU taxonomy)"""
        query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT DISTINCT ?concept ?prefLabel ?definition
        WHERE {
            ?concept rdf:type skos:Concept .
            ?concept skos:prefLabel ?prefLabel .
            OPTIONAL { ?concept skos:definition ?definition }
            FILTER(lang(?prefLabel) = "en")
        }
        LIMIT 500
        """
        
        self.sparql.setQuery(query)
        
        try:
            results = self.sparql.query().convert()
            concepts = []
            for result in results['results']['bindings']:
                concepts.append({
                    'uri': result.get('concept', {}).get('value', ''),
                    'label': result.get('prefLabel', {}).get('value', ''),
                    'definition': result.get('definition', {}).get('value', '')
                })
            return concepts
        except Exception as e:
            logger.error(f"Error fetching EuroVoc concepts: {e}")
            return []


# Alternative: Use eurlex-parser package
try:
    from eurlex import get_data_by_celex_id, get_summary_by_celex_id
    
    class EURexParserWrapper:
        """Wrapper for eurlex-parser package"""
        
        @staticmethod
        def get_document(celex_id: str, language: str = "en") -> Dict:
            """Get document data using eurlex-parser"""
            try:
                return get_data_by_celex_id(celex_id, language)
            except Exception as e:
                logger.error(f"Error parsing {celex_id}: {e}")
                return {}
        
        @staticmethod
        def get_summary(celex_id: str, language: str = "en") -> Dict:
            """Get document summary"""
            try:
                return get_summary_by_celex_id(celex_id, language)
            except Exception as e:
                logger.error(f"Error getting summary for {celex_id}: {e}")
                return {}
                
except ImportError:
    logger.warning("eurlex-parser not installed. Install with: pip install eurlex-parser")


# Example usage
if __name__ == "__main__":
    config = {
        'eurlex': {
            'sparql_endpoint': 'https://publications.europa.eu/webapi/rdf/sparql',
            'rest_endpoint': 'https://eur-lex.europa.eu/legal-content'
        }
    }
    
    fetcher = EUPolicyFetcher(config)
    policies = fetcher.fetch_policies(['REG'])
    print(f"Fetched {len(policies)} policies")
    print(policies.head())