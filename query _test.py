# query_databases.py - Query examples

import sqlite3
import json

def query_policies():
    """Query policies database"""
    conn = sqlite3.connect('data/policies.db')
    cursor = conn.cursor()
    
    # Get all policies
    cursor.execute('SELECT celex_id, title, type, date FROM policies')
    print("📋 All Policies:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} ({row[2]})")
    
    # Get policies by type
    cursor.execute("SELECT COUNT(*), type FROM policies GROUP BY type")
    print("\n📊 Policies by Type:")
    for row in cursor.fetchall():
        print(f"  - {row[1]}: {row[0]}")
    
    # Get policy with articles (GDPR)
    cursor.execute('''
        SELECT p.title, a.article_number, a.title, a.content
        FROM policies p
        JOIN policy_articles a ON p.id = a.policy_id
        WHERE p.celex_id = '32016R0679'
        ORDER BY a.article_number
    ''')
    print("\n📄 GDPR Articles:")
    for row in cursor.fetchall():
        print(f"  Art.{row[1]}: {row[2]}")
        print(f"    {row[3][:100]}...")
    
    conn.close()

def query_violations():
    """Query violations database"""
    conn = sqlite3.connect('data/violations.db')
    cursor = conn.cursor()
    
    # Get violation summary
    cursor.execute('''
        SELECT severity, COUNT(*) as count 
        FROM violations 
        GROUP BY severity 
        ORDER BY count DESC
    ''')
    print("\n📊 Violations by Severity:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    # Get unresolved violations
    cursor.execute('''
        SELECT type, source, severity, description 
        FROM violations 
        WHERE resolved = 0 
        ORDER BY severity DESC 
        LIMIT 10
    ''')
    print("\n⚠️ Unresolved Violations (Top 10):")
    for row in cursor.fetchall():
        print(f"  - [{row[2]}] {row[0]} in {row[1]}")
        print(f"    {row[3][:60]}...")
    
    # Get violations by source
    cursor.execute('''
        SELECT source, COUNT(*) as count 
        FROM violations 
        GROUP BY source 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    print("\n🌐 Sources with Most Violations:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    conn.close()

if __name__ == "__main__":
    query_policies()
    query_violations()