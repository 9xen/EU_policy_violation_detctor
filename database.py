"""
Database Module - Store policies and violations
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Policy(Base):
    """EU Policy Model"""
    __tablename__ = 'policies'
    
    id = Column(Integer, primary_key=True)
    celex_id = Column(String(50), unique=True)
    title = Column(String(500))
    type = Column(String(50))
    date = Column(DateTime)
    content = Column(Text)
    summary = Column(Text)
    eurovoc_concepts = Column(JSON)
    references = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Violation(Base):
    """Policy Violation Model"""
    __tablename__ = 'violations'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(100))
    source = Column(String(500))  # URL, repo, etc.
    policy_id = Column(Integer)
    severity = Column(String(20))
    description = Column(Text)
    evidence = Column(Text)
    similarity_score = Column(Float)
    detected_at = Column(DateTime, default=datetime.now)
    resolved = Column(Integer, default=0)
    resolution_note = Column(Text)

class PolicyDatabase:
    """Database manager for policies and violations"""
    
    def __init__(self, connection_string: str = 'sqlite:///data/policies.db'):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
    def add_policy(self, policy_data: Dict) -> int:
        """Add a policy to the database"""
        policy = Policy(
            celex_id=policy_data.get('celex_id'),
            title=policy_data.get('title'),
            type=policy_data.get('type'),
            date=policy_data.get('date'),
            content=policy_data.get('content'),
            summary=policy_data.get('summary', ''),
            eurovoc_concepts=policy_data.get('concepts', []),
            references=policy_data.get('references', [])
        )
        
        self.session.add(policy)
        self.session.commit()
        return policy.id
    
    def get_policy(self, celex_id: str) -> Dict:
        """Get a policy by CELEX ID"""
        policy = self.session.query(Policy).filter_by(celex_id=celex_id).first()
        if policy:
            return {
                'id': policy.id,
                'celex_id': policy.celex_id,
                'title': policy.title,
                'type': policy.type,
                'date': policy.date,
                'content': policy.content,
                'summary': policy.summary,
                'concepts': policy.eurovoc_concepts,
                'references': policy.references
            }
        return {}
    
    def get_all_policies(self) -> List[Dict]:
        """Get all policies"""
        policies = self.session.query(Policy).all()
        return [self._policy_to_dict(p) for p in policies]
    
    def _policy_to_dict(self, policy) -> Dict:
        """Convert policy to dictionary"""
        return {
            'id': policy.id,
            'celex_id': policy.celex_id,
            'title': policy.title,
            'type': policy.type,
            'date': policy.date.isoformat() if policy.date else '',
            'content': policy.content,
            'summary': policy.summary,
            'concepts': policy.eurovoc_concepts,
            'references': policy.references
        }
    
    def add_violation(self, violation_data: Dict) -> int:
        """Add a violation to the database"""
        violation = Violation(
            type=violation_data.get('type'),
            source=violation_data.get('source'),
            policy_id=violation_data.get('policy_id'),
            severity=violation_data.get('severity'),
            description=violation_data.get('description'),
            evidence=violation_data.get('evidence'),
            similarity_score=violation_data.get('similarity_score', 0.0)
        )
        
        self.session.add(violation)
        self.session.commit()
        return violation.id
    
    def get_violations(self, source: str = None) -> List[Dict]:
        """Get violations, optionally filtered by source"""
        query = self.session.query(Violation)
        if source:
            query = query.filter_by(source=source)
        
        violations = query.order_by(Violation.detected_at.desc()).all()
        
        return [{
            'id': v.id,
            'type': v.type,
            'source': v.source,
            'policy_id': v.policy_id,
            'severity': v.severity,
            'description': v.description,
            'evidence': v.evidence,
            'similarity_score': v.similarity_score,
            'detected_at': v.detected_at.isoformat(),
            'resolved': bool(v.resolved)
        } for v in violations]
    
    def resolve_violation(self, violation_id: int, note: str = '') -> bool:
        """Mark a violation as resolved"""
        violation = self.session.query(Violation).filter_by(id=violation_id).first()
        if violation:
            violation.resolved = 1
            violation.resolution_note = note
            self.session.commit()
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        policies_count = self.session.query(Policy).count()
        violations_count = self.session.query(Violation).count()
        unresolved_count = self.session.query(Violation).filter_by(resolved=0).count()
        
        return {
            'total_policies': policies_count,
            'total_violations': violations_count,
            'unresolved_violations': unresolved_count,
            'resolution_rate': round((1 - unresolved_count/violations_count) * 100, 2) if violations_count > 0 else 0
        }
    
    def close(self):
        """Close database connection"""
        self.session.close()


# Example usage
if __name__ == "__main__":
    db = PolicyDatabase()
    
    # Add a sample policy
    policy_id = db.add_policy({
        'celex_id': '32024R1689',
        'title': 'AI Act',
        'type': 'REG',
        'date': datetime.now(),
        'content': 'Full AI Act text...',
        'summary': 'Regulation on artificial intelligence',
        'concepts': ['AI', 'regulation'],
        'references': ['GDPR', 'other policies']
    })
    print(f"Added policy ID: {policy_id}")
    
    # Add a sample violation
    violation_id = db.add_violation({
        'type': 'DATA_PRIVACY',
        'source': 'https://example.com',
        'policy_id': policy_id,
        'severity': 'HIGH',
        'description': 'Personal data collected without consent',
        'evidence': 'Privacy policy page missing',
        'similarity_score': 0.85
    })
    print(f"Added violation ID: {violation_id}")
    
    # Get stats
    stats = db.get_stats()
    print(f"Statistics: {stats}")
    
    db.close()