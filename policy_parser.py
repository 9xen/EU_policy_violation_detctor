"""
Policy Parser - Parse and structure EU policy documents
"""

import re
from typing import Dict, List, Optional
import pandas as pd
from bs4 import BeautifulSoup
import logging
from sentence_transformers import SentenceTransformer
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyParser:
    """Parse EU policy documents and extract key information"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.policy_cache = {}
        
    def parse_content(self, html_content: str) -> Dict:
        """Parse HTML content of a policy document"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract main sections
        result = {
            'title': self._extract_title(soup),
            'preamble': self._extract_preamble(soup),
            'articles': self._extract_articles(soup),
            'annexes': self._extract_annexes(soup),
            'references': self._extract_references(soup),
            'keywords': self._extract_keywords(soup)
        }
        
        return result
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract document title"""
        title_elem = soup.find('h1')
        return title_elem.text.strip() if title_elem else ""
    
    def _extract_preamble(self, soup: BeautifulSoup) -> str:
        """Extract preamble/recitals"""
        preamble = []
        for p in soup.find_all('p'):
            text = p.text.strip()
            if text.startswith('(1)') or text.startswith('1.'):
                preamble.append(text)
        return '\n'.join(preamble)
    
    def _extract_articles(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract articles with their content"""
        articles = []
        
        # Find article elements
        article_pattern = re.compile(r'Article\s+(\d+)', re.IGNORECASE)
        
        for elem in soup.find_all(['p', 'div', 'section']):
            text = elem.text.strip()
            match = article_pattern.match(text)
            
            if match:
                article_num = match.group(1)
                content = text.replace(f'Article {article_num}', '').strip()
                
                articles.append({
                    'number': int(article_num),
                    'title': self._extract_article_title(elem),
                    'content': content,
                    'html': str(elem)
                })
        
        return articles
    
    def _extract_article_title(self, elem) -> str:
        """Extract article title"""
        # Look for title in bold/heading
        for child in elem.children:
            if hasattr(child, 'name') and child.name in ['b', 'strong', 'h2', 'h3']:
                return child.text.strip()
        return ""
    
    def _extract_annexes(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract annexes"""
        annexes = []
        current_annex = None
        
        for elem in soup.find_all(['p', 'div']):
            text = elem.text.strip()
            if 'ANNEX' in text.upper() or 'ANEXO' in text.upper():
                if current_annex:
                    annexes.append(current_annex)
                current_annex = {'title': text, 'content': []}
            elif current_annex:
                current_annex['content'].append(text)
        
        if current_annex:
            annexes.append(current_annex)
        
        return annexes
    
    def _extract_references(self, soup: BeautifulSoup) -> List[str]:
        """Extract references to other documents"""
        references = []
        
        # Look for CELEX numbers
        celex_pattern = re.compile(r'\d{4}[A-Z]{1,2}\d{1,5}')
        
        for text in soup.stripped_strings:
            matches = celex_pattern.findall(text)
            references.extend(matches)
        
        return list(set(references))
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords/topics"""
        keywords = []
        
        # Look for EuroVoc terms
        eurovoc_pattern = re.compile(r'EuroVoc\s*:\s*(.*?)(?:\n|$)')
        for text in soup.stripped_strings:
            match = eurovoc_pattern.search(text)
            if match:
                terms = match.group(1).split(',')
                keywords.extend([t.strip() for t in terms])
        
        return keywords
    
    def extract_policy_requirements(self, parsed_doc: Dict) -> List[Dict]:
        """Extract specific requirements/obligations from policy"""
        requirements = []
        
        # Extract from articles
        for article in parsed_doc.get('articles', []):
            # Look for obligation keywords
            obligation_patterns = [
                r'shall\s+(\w+\s+\w+)',
                r'must\s+(\w+\s+\w+)',
                r'is\s+required\s+to\s+(\w+\s+\w+)',
                r'obligation\s+to\s+(\w+\s+\w+)',
                r'subject\s+to\s+(\w+\s+\w+)'
            ]
            
            content = article.get('content', '')
            
            for pattern in obligation_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    requirements.append({
                        'article': article.get('number'),
                        'requirement': match.strip(),
                        'full_text': content
                    })
        
        return requirements
    
    def create_policy_embeddings(self, policies: List[Dict]) -> Dict:
        """Create embeddings for policy documents"""
        embeddings = {}
        
        for policy in policies:
            # Combine title and content for embedding
            text = f"{policy.get('title', '')} {policy.get('content', '')}"
            embedding = self.model.encode(text)
            embeddings[policy.get('celex_id', '')] = embedding
        
        return embeddings
    
    def save_embeddings(self, embeddings: Dict, path: str = 'models/policy_embeddings.pkl'):
        """Save policy embeddings"""
        joblib.dump(embeddings, path)
        logger.info(f"Saved embeddings to {path}")


# Alternative: Use eurlex-parser for structured extraction
try:
    from eurlex import get_data_by_celex_id, get_articles_by_celex_id
    
    class EURexParser:
        """Structured parser using eurlex-parser"""
        
        @staticmethod
        def parse_document(celex_id: str) -> Dict:
            """Parse document into structured format"""
            try:
                return get_data_by_celex_id(celex_id)
            except Exception as e:
                logger.error(f"Error parsing {celex_id}: {e}")
                return {}
        
        @staticmethod
        def get_articles_df(celex_id: str) -> pd.DataFrame:
            """Get articles as DataFrame"""
            try:
                return get_articles_by_celex_id(celex_id)
            except Exception as e:
                logger.error(f"Error getting articles for {celex_id}: {e}")
                return pd.DataFrame()
                
except ImportError:
    logger.warning("eurlex-parser not installed")