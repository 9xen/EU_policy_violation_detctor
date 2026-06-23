"""
GitHub Scanner - Scan GitHub repositories for policy violations
"""

from github import Github, GithubException
from typing import List, Dict, Optional
import re
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubScanner:
    """Scan GitHub repositories for policy violations"""
    
    def __init__(self, token: str = None):
        self.token = token
        self.client = Github(token) if token else Github()
        self.violations = []
        
    def scan_repo(self, repo_name: str) -> List[Dict]:
        """Scan a repository for policy violations"""
        logger.info(f"Scanning repository: {repo_name}")
        
        try:
            repo = self.client.get_repo(repo_name)
            
            # Check repository for violations
            violations = []
            
            # Check license
            if not repo.license:
                violations.append({
                    'type': 'LICENSE',
                    'repo': repo_name,
                    'severity': 'MEDIUM',
                    'description': 'No license found',
                    'evidence': 'Repository has no LICENSE file'
                })
            
            # Check README
            if not repo.readme:
                violations.append({
                    'type': 'DOCUMENTATION',
                    'repo': repo_name,
                    'severity': 'LOW',
                    'description': 'No README found',
                    'evidence': 'Repository has no README file'
                })
            
            # Check for sensitive data in code
            sensitive_patterns = {
                'API_KEY': r'(api|access|secret)_?key\s*=\s*[\"\']?[a-zA-Z0-9_\-]{10,}',
                'PASSWORD': r'password\s*=\s*[\"\']?[^\s\"]+',
                'TOKEN': r'token\s*=\s*[\"\']?[a-zA-Z0-9_\-]{20,}',
                'AWS_KEY': r'AKIA[0-9A-Z]{16}',
                'PRIVATE_KEY': r'-----BEGIN.*PRIVATE KEY-----'
            }
            
            # Scan files for sensitive data
            try:
                contents = repo.get_contents('')
                for content in contents:
                    if content.type == 'file':
                        file_content = content.decoded_content.decode('utf-8', errors='ignore')
                        
                        for pattern_name, pattern in sensitive_patterns.items():
                            if re.search(pattern, file_content, re.IGNORECASE):
                                violations.append({
                                    'type': 'SENSITIVE_DATA',
                                    'repo': repo_name,
                                    'file': content.path,
                                    'pattern': pattern_name,
                                    'severity': 'HIGH',
                                    'description': f'Potential {pattern_name} exposure found'
                                })
                                
            except Exception as e:
                logger.error(f"Error scanning files: {e}")
            
            # Check for EU policy compliance
            eu_keywords = ['gdpr', 'privacy', 'data-protection']
            code_text = ' '.join([c.path for c in contents]) if contents else ''
            
            if not any(keyword in code_text.lower() for keyword in eu_keywords):
                violations.append({
                    'type': 'EU_COMPLIANCE',
                    'repo': repo_name,
                    'severity': 'LOW',
                    'description': 'No EU policy compliance mentions',
                    'evidence': 'No GDPR or data protection references found'
                })
            
            self.violations.extend(violations)
            return violations
            
        except GithubException as e:
            logger.error(f"Error scanning {repo_name}: {e}")
            return []
    
    def search_repos(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search for repositories"""
        results = []
        
        try:
            repos = self.client.search_repositories(query)
            
            for repo in repos[:max_results]:
                results.append({
                    'name': repo.full_name,
                    'url': repo.html_url,
                    'description': repo.description,
                    'created_at': repo.created_at,
                    'updated_at': repo.updated_at,
                    'stars': repo.stargazers_count
                })
                
        except Exception as e:
            logger.error(f"Error searching repositories: {e}")
        
        return results
    
    def scan_organization(self, org_name: str) -> List[Dict]:
        """Scan all repositories in an organization"""
        violations = []
        
        try:
            org = self.client.get_organization(org_name)
            repos = org.get_repos()
            
            for repo in repos:
                repo_violations = self.scan_repo(repo.full_name)
                violations.extend(repo_violations)
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error scanning organization {org_name}: {e}")
        
        return violations
    
    def get_compliance_report(self, repo_name: str) -> Dict:
        """Get a compliance report for a repository"""
        violations = self.scan_repo(repo_name)
        
        report = {
            'repo': repo_name,
            'scan_date': datetime.now().isoformat(),
            'violations': violations,
            'violation_count': len(violations),
            'severity_summary': self._summarize_severities(violations),
            'recommendations': self._generate_recommendations(violations)
        }
        
        return report
    
    def _summarize_severities(self, violations: List[Dict]) -> Dict:
        """Summarize violations by severity"""
        summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for v in violations:
            severity = v.get('severity', 'LOW')
            summary[severity] = summary.get(severity, 0) + 1
        return summary
    
    def _generate_recommendations(self, violations: List[Dict]) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        
        violation_types = set(v.get('type') for v in violations)
        
        if 'LICENSE' in violation_types:
            recommendations.append("Add a license file (MIT, Apache, or GPL)")
        
        if 'SENSITIVE_DATA' in violation_types:
            recommendations.append("Remove sensitive data from repository")
            recommendations.append("Use environment variables or secret management")
        
        if 'DOCUMENTATION' in violation_types:
            recommendations.append("Add README.md with project documentation")
        
        if 'EU_COMPLIANCE' in violation_types:
            recommendations.append("Add GDPR/privacy compliance statements")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    scanner = GitHubScanner()
    
    # Scan a repository
    violations = scanner.scan_repo("openai/gpt-3")
    print(f"Found {len(violations)} violations")
    
    # Get compliance report
    report = scanner.get_compliance_report("openai/gpt-3")
    print(json.dumps(report, indent=2))