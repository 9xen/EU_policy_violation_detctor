"""
Main Application - EU Policy Monitor
"""

import yaml
import logging
from pathlib import Path
from datetime import datetime
import json

from policy_fetcher import EUPolicyFetcher
from policy_parser import PolicyParser
from violation_detector import PolicyViolationDetector
from web_scanner import WebScanner
from github_scanner import GitHubScanner
from database import PolicyDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EUPolicyMonitor:
    """Main application class"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        self.config = self._load_config(config_path)
        self.db = PolicyDatabase(self.config['database']['connection_string'])
        self.fetcher = EUPolicyFetcher(self.config)
        self.parser = PolicyParser()
        self.detector = PolicyViolationDetector()
        
    def _load_config(self, path: str) -> Dict:
        """Load configuration"""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def fetch_policies(self):
        """Fetch all policies from EU sources"""
        logger.info("Fetching policies...")
        
        policy_types = self.config.get('policy_types', ['REG', 'DIR', 'DEC'])
        policies_df = self.fetcher.fetch_policies(policy_types)
        
        for _, row in policies_df.iterrows():
            # Check if policy exists
            existing = self.db.get_policy(row.get('celex_id', ''))
            if not existing:
                self.db.add_policy(row.to_dict())
                logger.info(f"Added policy: {row.get('celex_id')}")
        
        logger.info(f"Fetched {len(policies_df)} policies")
        return policies_df
    
    def scan_website(self, url: str):
        """Scan a website for policy violations"""
        logger.info(f"Scanning website: {url}")
        
        scanner = WebScanner(self.config)
        violations = scanner.scan_website(url)
        
        for violation in violations:
            self.db.add_violation({
                **violation,
                'source': url,
                'type': violation.get('type', 'WEBSITE'),
                'detected_at': datetime.now()
            })
        
        logger.info(f"Found {len(violations)} violations")
        return violations
    
    def scan_github(self, repo: str):
        """Scan a GitHub repository"""
        logger.info(f"Scanning GitHub repo: {repo}")
        
        token = self.config.get('github', {}).get('token')
        scanner = GitHubScanner(token)
        violations = scanner.scan_repo(repo)
        
        for violation in violations:
            self.db.add_violation({
                **violation,
                'source': repo,
                'detected_at': datetime.now()
            })
        
        logger.info(f"Found {len(violations)} violations")
        return violations
    
    def analyze_text(self, text: str):
        """Analyze text for policy violations"""
        logger.info("Analyzing text for violations...")
        
        policies = self.db.get_all_policies()
        violations = self.detector.detect_violation(text, policies)
        
        for violation in violations:
            self.db.add_violation({
                **violation,
                'source': 'TEXT_ANALYSIS',
                'detected_at': datetime.now()
            })
        
        return violations
    
    def get_report(self) -> Dict:
        """Get overall compliance report"""
        stats = self.db.get_stats()
        violations = self.db.get_violations()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'recent_violations': violations[:10],
            'summary': self._generate_summary(stats)
        }
    
    def _generate_summary(self, stats: Dict) -> str:
        """Generate a human-readable summary"""
        return f"""
        EU Policy Monitor Report
        =========================
        Total Policies: {stats['total_policies']}
        Total Violations: {stats['total_violations']}
        Unresolved: {stats['unresolved_violations']}
        Resolution Rate: {stats['resolution_rate']}%
        """


# CLI Interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='EU Policy Monitor')
    parser.add_argument('--fetch', action='store_true', help='Fetch policies')
    parser.add_argument('--scan-web', type=str, help='Scan a website')
    parser.add_argument('--scan-github', type=str, help='Scan a GitHub repo')
    parser.add_argument('--analyze', type=str, help='Analyze text')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--config', type=str, default='config.yaml', help='Config file')
    
    args = parser.parse_args()
    
    monitor = EUPolicyMonitor(args.config)
    
    if args.fetch:
        monitor.fetch_policies()
    
    if args.scan_web:
        monitor.scan_website(args.scan_web)
    
    if args.scan_github:
        monitor.scan_github(args.scan_github)
    
    if args.analyze:
        with open(args.analyze, 'r') as f:
            text = f.read()
        monitor.analyze_text(text)
    
    if args.report:
        report = monitor.get_report()
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()