"""
Database Setup - Create and initialize database files
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

def create_database_structure():
    """Create both database files with proper structure"""
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Create policies.db
    create_policies_db()
    
    # Create violations.db
    create_violations_db()
    
    print("✅ Database files created successfully!")
    print("📁 policies.db created with structure")
    print("📁 violations.db created with structure")

def create_policies_db():
    """Create policies database with tables"""
    conn = sqlite3.connect('data/policies.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            celex_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            date TEXT,
            content TEXT,
            summary TEXT,
            eurovoc_concepts TEXT,
            references TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eurovoc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_id TEXT UNIQUE,
            label TEXT,
            definition TEXT,
            policy_id INTEGER,
            FOREIGN KEY (policy_id) REFERENCES policies(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policy_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER,
            article_number INTEGER,
            title TEXT,
            content TEXT,
            FOREIGN KEY (policy_id) REFERENCES policies(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policy_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER,
            reference_type TEXT,
            reference_id TEXT,
            FOREIGN KEY (policy_id) REFERENCES policies(id)
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX idx_policies_celex ON policies(celex_id);
        CREATE INDEX idx_policies_type ON policies(type);
    ''')
    
    conn.commit()
    conn.close()
    print("✅ policies.db structure created")

def create_violations_db():
    """Create violations database with tables"""
    conn = sqlite3.connect('data/violations.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            source TEXT NOT NULL,
            policy_id INTEGER,
            severity TEXT NOT NULL,
            description TEXT,
            evidence TEXT,
            similarity_score REAL,
            detected_at TEXT,
            resolved INTEGER DEFAULT 0,
            resolution_note TEXT,
            resolved_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_type TEXT NOT NULL,
            target TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            status TEXT,
            violations_found INTEGER DEFAULT 0,
            scan_data TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compliance_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT UNIQUE NOT NULL,
            generated_at TEXT,
            summary TEXT,
            score INTEGER,
            violations_json TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX idx_violations_source ON violations(source);
        CREATE INDEX idx_violations_severity ON violations(severity);
        CREATE INDEX idx_violations_detected ON violations(detected_at);
        CREATE INDEX idx_scans_target ON scans(target);
    ''')
    
    conn.commit()
    conn.close()
    print("✅ violations.db structure created")

def populate_sample_data():
    """Populate databases with sample EU policy data"""
    
    # Sample EU policies (GDPR, AI Act, etc.)
    sample_policies = [
        {
            'celex_id': '32016R0679',
            'title': 'General Data Protection Regulation (GDPR)',
            'type': 'REG',
            'date': '2016-04-27',
            'summary': 'Regulation on the protection of natural persons with regard to the processing of personal data',
            'concepts': ['data protection', 'privacy', 'personal data', 'consent'],
            'references': ['Directive 95/46/EC']
        },
        {
            'celex_id': '32024R1689',
            'title': 'Artificial Intelligence Act (AI Act)',
            'type': 'REG',
            'date': '2024-03-13',
            'summary': 'Regulation laying down harmonised rules on artificial intelligence',
            'concepts': ['AI', 'machine learning', 'risk classification', 'transparency'],
            'references': ['GDPR', 'Directive 2016/680']
        },
        {
            'celex_id': '32018L1972',
            'title': 'European Electronic Communications Code',
            'type': 'DIR',
            'date': '2018-12-11',
            'summary': 'Directive establishing the European Electronic Communications Code',
            'concepts': ['telecommunications', 'net neutrality', '5G', 'connectivity'],
            'references': ['Directive 2002/21/EC']
        },
        {
            'celex_id': '32023R2855',
            'title': 'Digital Services Act',
            'type': 'REG',
            'date': '2023-10-19',
            'summary': 'Regulation on a Single Market For Digital Services',
            'concepts': ['online platforms', 'content moderation', 'transparency', 'user protection'],
            'references': ['Directive 2000/31/EC']
        },
        {
            'celex_id': '32024R0980',
            'title': 'Cyber Resilience Act',
            'type': 'REG',
            'date': '2024-03-10',
            'summary': 'Regulation on cybersecurity requirements for products with digital elements',
            'concepts': ['cybersecurity', 'digital products', 'vulnerabilities', 'incident reporting'],
            'references': ['Regulation 2019/881']
        },
        {
            'celex_id': '32024R0001',
            'title': 'Data Act',
            'type': 'REG',
            'date': '2024-01-11',
            'summary': 'Regulation on harmonised rules on fair access to and use of data',
            'concepts': ['data sharing', 'data access', 'IoT', 'cloud computing'],
            'references': ['GDPR', 'Open Data Directive']
        },
        {
            'celex_id': '32023R0455',
            'title': 'Digital Markets Act',
            'type': 'REG',
            'date': '2023-05-02',
            'summary': 'Regulation on contestable and fair markets in the digital sector',
            'concepts': ['gatekeepers', 'competition', 'interoperability', 'fairness'],
            'references': ['Regulation 2019/1150']
        },
        {
            'celex_id': '32024R1347',
            'title': 'Green Deal Industrial Plan',
            'type': 'DEC',
            'date': '2024-02-28',
            'summary': 'Decision on the European Green Deal industrial strategy',
            'concepts': ['climate', 'net-zero', 'green transition', 'sustainability'],
            'references': ['European Green Deal']
        },
        {
            'celex_id': '32023R0245',
            'title': 'European Health Data Space',
            'type': 'REG',
            'date': '2023-12-15',
            'summary': 'Regulation establishing a European Health Data Space',
            'concepts': ['health data', 'patient records', 'healthcare', 'data sharing'],
            'references': ['GDPR']
        },
        {
            'celex_id': '32024R0002',
            'title': 'ESG Disclosure Regulation',
            'type': 'REG',
            'date': '2024-01-15',
            'summary': 'Regulation on Environmental, Social and Governance disclosure',
            'concepts': ['ESG', 'sustainability', 'disclosure', 'greenwashing'],
            'references': ['SFDR', 'Taxonomy Regulation']
        }
    ]
    
    conn = sqlite3.connect('data/policies.db')
    cursor = conn.cursor()
    
    for policy in sample_policies:
        cursor.execute('''
            INSERT OR IGNORE INTO policies 
            (celex_id, title, type, date, content, summary, eurovoc_concepts, references, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            policy['celex_id'],
            policy['title'],
            policy['type'],
            policy['date'],
            f"Full text of {policy['title']}...",  # Placeholder content
            policy['summary'],
            json.dumps(policy['concepts']),
            json.dumps(policy['references']),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Get the policy ID
        policy_id = cursor.lastrowid
        
        # Add sample articles for GDPR (if it's the GDPR policy)
        if policy['celex_id'] == '32016R0679':
            articles = [
                {'num': 1, 'title': 'Subject-matter and objectives', 
                 'content': 'This Regulation lays down rules relating to the protection of natural persons with regard to the processing of personal data.'},
                {'num': 4, 'title': 'Definitions', 
                 'content': 'For the purposes of this Regulation: "personal data" means any information relating to an identified or identifiable natural person...'},
                {'num': 5, 'title': 'Principles relating to processing of personal data', 
                 'content': 'Personal data shall be: (a) processed lawfully, fairly and in a transparent manner; (b) collected for specified, explicit and legitimate purposes;'},
                {'num': 6, 'title': 'Lawfulness of processing', 
                 'content': 'Processing shall be lawful only if and to the extent that at least one of the following applies: (a) the data subject has given consent;'},
                {'num': 7, 'title': 'Conditions for consent', 
                 'content': 'Where processing is based on consent, the controller shall be able to demonstrate that the data subject has consented to processing of his or her personal data.'},
                {'num': 32, 'title': 'Data protection by design and by default', 
                 'content': 'The controller shall implement appropriate technical and organisational measures to ensure that, by default, only personal data which are necessary for each specific purpose of the processing are processed.'}
            ]
            
            for article in articles:
                cursor.execute('''
                    INSERT INTO policy_articles (policy_id, article_number, title, content)
                    VALUES (?, ?, ?, ?)
                ''', (policy_id, article['num'], article['title'], article['content']))
        
        # Add sample articles for AI Act
        if policy['celex_id'] == '32024R1689':
            articles = [
                {'num': 1, 'title': 'Subject matter', 
                 'content': 'This Regulation lays down harmonised rules for the development, placing on the market and use of AI systems in the Union.'},
                {'num': 3, 'title': 'Definitions', 
                 'content': 'For the purposes of this Regulation: "AI system" means a machine-based system designed to operate with varying levels of autonomy.'},
                {'num': 5, 'title': 'Prohibited AI practices', 
                 'content': 'The following AI practices shall be prohibited: (a) placing on the market of AI systems that deploy subliminal techniques;'},
                {'num': 9, 'title': 'Risk classification', 
                 'content': 'AI systems shall be classified as unacceptable risk, high risk, or limited risk based on their potential impact.'}
            ]
            
            for article in articles:
                cursor.execute('''
                    INSERT INTO policy_articles (policy_id, article_number, title, content)
                    VALUES (?, ?, ?, ?)
                ''', (policy_id, article['num'], article['title'], article['content']))
    
    conn.commit()
    conn.close()
    print(f"✅ Added {len(sample_policies)} sample policies to policies.db")

def populate_violations():
    """Populate violations database with sample data"""
    
    violation_types = [
        'DATA_PRIVACY', 'SECURITY', 'ACCESSIBILITY', 'CONSUMER_PROTECTION',
        'AI_COMPLIANCE', 'GDPR_VIOLATION', 'DIGITAL_SERVICES', 'CYBERSECURITY',
        'ENVIRONMENTAL', 'COMPETITION', 'DATA_SHARING', 'ESG_DISCLOSURE'
    ]
    
    severities = ['HIGH', 'MEDIUM', 'LOW']
    sources = [
        'https://example.com', 'https://test-site.com', 'https://ecommerce-store.com',
        'https://github.com/user/repo1', 'https://github.com/org/repo2',
        'https://erp-system.com/admin', 'https://cms-platform.com/dashboard',
        'https://api-service.com/v1', 'https://cloud-app.com/userdata'
    ]
    
    conn = sqlite3.connect('data/violations.db')
    cursor = conn.cursor()
    
    # Generate 50 sample violations
    for i in range(50):
        violation_type = random.choice(violation_types)
        severity = random.choice(severities)
        source = random.choice(sources)
        detected_date = datetime.now() - timedelta(days=random.randint(0, 30))
        resolved = random.choice([0, 0, 0, 1])  # 25% resolved
        
        descriptions = {
            'DATA_PRIVACY': 'Personal data collected without proper consent',
            'SECURITY': 'Sensitive data exposed in source code',
            'ACCESSIBILITY': 'Website not accessible for users with disabilities',
            'CONSUMER_PROTECTION': 'Misleading product descriptions found',
            'AI_COMPLIANCE': 'AI system uses prohibited subliminal techniques',
            'GDPR_VIOLATION': 'Data subject rights not properly addressed',
            'DIGITAL_SERVICES': 'Content moderation practices not transparent',
            'CYBERSECURITY': 'Vulnerabilities found in software components',
            'ENVIRONMENTAL': 'Insufficient environmental disclosure',
            'COMPETITION': 'Anti-competitive practices identified',
            'DATA_SHARING': 'Unauthorized data sharing with third parties',
            'ESG_DISCLOSURE': 'Incomplete ESG reporting'
        }
        
        evidence_examples = {
            'DATA_PRIVACY': 'Privacy policy page missing consent form',
            'SECURITY': 'API key found in public repository',
            'ACCESSIBILITY': 'Images missing alt text attributes',
            'CONSUMER_PROTECTION': 'False advertising claims on product page',
            'AI_COMPLIANCE': 'Bias detected in AI decision-making',
            'GDPR_VIOLATION': 'No opt-out mechanism for data sharing',
            'DIGITAL_SERVICES': 'Terms of service not clearly displayed',
            'CYBERSECURITY': 'Outdated dependencies with known vulnerabilities',
            'ENVIRONMENTAL': 'Carbon emissions data not reported',
            'COMPETITION': 'Market dominance abusive practices',
            'DATA_SHARING': 'Data sold to third parties without notice',
            'ESG_DISCLOSURE': 'ESG metrics not published in annual report'
        }
        
        cursor.execute('''
            INSERT INTO violations 
            (type, source, policy_id, severity, description, evidence, similarity_score, detected_at, resolved, resolution_note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            violation_type,
            source,
            random.randint(1, 10),  # Random policy_id
            severity,
            descriptions.get(violation_type, 'Policy violation detected'),
            evidence_examples.get(violation_type, 'Evidence found in content'),
            round(random.uniform(0.7, 0.98), 3),
            detected_date.isoformat(),
            resolved,
            'Issue resolved' if resolved else ''
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Added 50 sample violations to violations.db")

def create_sample_scans():
    """Add sample scan records"""
    
    conn = sqlite3.connect('data/violations.db')
    cursor = conn.cursor()
    
    scan_types = ['WEBSITE', 'GITHUB', 'ERP', 'CMS', 'API']
    targets = [
        'https://example.com', 'https://test-site.com',
        'github.com/org/repo', 'https://erp-system.com',
        'https://cms-platform.com', 'https://api-service.com'
    ]
    statuses = ['COMPLETED', 'COMPLETED', 'COMPLETED', 'FAILED', 'RUNNING']
    
    for _ in range(20):
        scan_type = random.choice(scan_types)
        target = random.choice(targets)
        started = datetime.now() - timedelta(hours=random.randint(0, 72))
        completed = started + timedelta(hours=random.randint(1, 6))
        status = random.choice(statuses)
        violations = random.randint(0, 15)
        
        cursor.execute('''
            INSERT INTO scans 
            (scan_type, target, started_at, completed_at, status, violations_found)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (scan_type, target, started.isoformat(), 
              completed.isoformat() if status != 'RUNNING' else None,
              status, violations))
    
    conn.commit()
    conn.close()
    print("✅ Added sample scan records")

def generate_all():
    """Generate all databases with sample data"""
    print("🔄 Creating database structure...")
    create_database_structure()
    
    print("🔄 Populating policies database...")
    populate_sample_data()
    
    print("🔄 Populating violations database...")
    populate_violations()
    create_sample_scans()
    
    # Verify databases exist
    if os.path.exists('data/policies.db') and os.path.exists('data/violations.db'):
        print("\n✅ SUCCESS! Database files created:")
        print(f"   - policies.db: {os.path.getsize('data/policies.db') / 1024:.2f} KB")
        print(f"   - violations.db: {os.path.getsize('data/violations.db') / 1024:.2f} KB")
        
        # Show summary
        conn = sqlite3.connect('data/policies.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM policies')
        policy_count = cursor.fetchone()[0]
        conn.close()
        
        conn = sqlite3.connect('data/violations.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM violations')
        violation_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"\n📊 Database Summary:")
        print(f"   - Policies: {policy_count}")
        print(f"   - Violations: {violation_count}")
    else:
        print("❌ Error creating databases")

def verify_databases():
    """Verify database integrity"""
    print("\n🔍 Verifying databases...")
    
    # Verify policies.db
    conn = sqlite3.connect('data/policies.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"📁 policies.db tables: {[t[0] for t in tables]}")
    
    cursor.execute("SELECT COUNT(*) FROM policies")
    count = cursor.fetchone()[0]
    print(f"   - Policies count: {count}")
    
    conn.close()
    
    # Verify violations.db
    conn = sqlite3.connect('data/violations.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"📁 violations.db tables: {[t[0] for t in tables]}")
    
    cursor.execute("SELECT COUNT(*) FROM violations")
    count = cursor.fetchone()[0]
    print(f"   - Violations count: {count}")
    
    cursor.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity")
    severity_counts = cursor.fetchall()
    for severity, count in severity_counts:
        print(f"   - {severity}: {count}")
    
    conn.close()

if __name__ == "__main__":
    generate_all()
    verify_databases()