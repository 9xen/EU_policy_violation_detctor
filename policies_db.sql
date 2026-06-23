-- policies.db structure and sample data

-- Table: policies
SELECT * FROM policies;

-- Sample data from policies.db
-- id | celex_id     | title                                    | type | date       | summary
-- ---|--------------|------------------------------------------|------|------------|----------------------------------------
-- 1  | 32016R0679   | General Data Protection Regulation (GDPR)| REG  | 2016-04-27 | Regulation on protection of personal data
-- 2  | 32024R1689   | Artificial Intelligence Act (AI Act)     | REG  | 2024-03-13 | Regulation on harmonised rules on AI
-- 3  | 32018L1972   | European Electronic Communications Code  | DIR  | 2018-12-11 | Directive on electronic communications
-- 4  | 32023R2855   | Digital Services Act                    | REG  | 2023-10-19 | Regulation on Single Market for Digital Services
-- 5  | 32024R0980   | Cyber Resilience Act                    | REG  | 2024-03-10 | Regulation on cybersecurity requirements

-- Table: policy_articles
SELECT * FROM policy_articles;

-- Sample articles for GDPR (policy_id=1)
-- id | policy_id | article_number | title                                    | content
-- ---|-----------|----------------|------------------------------------------|----------------------------------------
-- 1  | 1         | 1              | Subject-matter and objectives            | This Regulation lays down rules...
-- 2  | 1         | 4              | Definitions                              | "personal data" means any information...
-- 3  | 1         | 5              | Principles relating to processing        | Personal data shall be: (a) processed...

-- Table: eurovoc
-- (empty initially, can be populated)

-- Table: policy_references
-- (empty initially, can be populated)