# Step 1: Create directories
mkdir -p data models src

# Step 2: Setup databases
python src/database_setup.py

# Step 3: Train all models
python src/model_trainer.py

# Step 4: Verify models
python verify_models.py

# Step 5: Test models
python -c "
from src.model_loader import ModelLoader
loader = ModelLoader()
text = 'This website collects user data without consent'
result = loader.detect_violation(text)
print(f'Result: {result}')
"