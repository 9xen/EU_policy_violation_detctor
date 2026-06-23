# Step 1: Create the data directory
mkdir -p data

# Step 2: Run the database setup script
python src/database_setup.py

# Step 3: Verify databases were created
ls -lh data/
# Output:
# -rw-r--r-- 1 user user  28K Jun 23 14:30 policies.db
# -rw-r--r-- 1 user user  24K Jun 23 14:30 violations.db

# Step 4: Query the databases
python query_databases.py