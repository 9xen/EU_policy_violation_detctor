"""
Model Loader - Load and use trained models
"""

import joblib
import numpy as np
from typing import List, Dict, Optional
import os

class ModelLoader:
    """Load and use trained models"""
    
    def __init__(self):
        self.models_dir = 'models'
        self.violation_model = None
        self.embeddings = None
        self.similarity_model = None
        self.classifier = None
        
        self.load_all_models()
    
    def load_all_models(self):
        """Load all trained models"""
        print("🔄 Loading models...")
        
        # Load violation model
        try:
            self.violation_model = joblib.load(
                os.path.join(self.models_dir, 'violation_model.pkl')
            )
            print("✅ Violation model loaded")
        except Exception as e:
            print(f"❌ Error loading violation model: {e}")
        
        # Load embeddings
        try:
            self.embeddings = joblib.load(
                os.path.join(self.models_dir, 'policy_embeddings.pkl')
            )
            print(f"✅ Embeddings loaded ({len(self.embeddings['policies'])} policies)")
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
        
        # Load similarity model
        try:
            self.similarity_model = joblib.load(
                os.path.join(self.models_dir, 'similarity_model.pkl')
            )
            print("✅ Similarity model loaded")
        except Exception as e:
            print(f"❌ Error loading similarity model: {e}")
        
        # Load classifier
        try:
            self.classifier = joblib.load(
                os.path.join(self.models_dir, 'classifier_model.pkl')
            )
            print(f"✅ Classifier loaded ({len(self.classifier['classes'])} classes)")
        except Exception as e:
            print(f"❌ Error loading classifier: {e}")
    
    def detect_violation(self, text: str) -> Dict:
        """Detect policy violation in text"""
        if self.violation_model is None:
            return {'error': 'Model not loaded'}
        
        model_data = self.violation_model
        vectorizer = model_data['vectorizer']
        model = model_data['model']
        
        # Vectorize text
        X = vectorizer.transform([text])
        
        # Predict
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        # Get class probabilities
        classes = model_data['classes']
        class_probs = {classes[i]: prob for i, prob in enumerate(probabilities)}
        
        return {
            'category': prediction,
            'confidence': max(probabilities),
            'all_probabilities': class_probs,
            'is_violation': prediction != 'COMPLIANT'
        }
    
    def find_similar_policies(self, text: str, top_k: int = 5) -> List[Dict]:
        """Find policies similar to the given text"""
        if self.embeddings is None:
            return []
        
        # Get text embedding
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        text_embedding = embedder.encode(text)
        
        # Calculate similarities with all policies
        similarities = []
        for policy in self.embeddings['policies']:
            policy_embedding = policy['embedding']
            similarity = np.dot(text_embedding, policy_embedding) / (
                np.linalg.norm(text_embedding) * np.linalg.norm(policy_embedding)
            )
            similarities.append({
                'celex_id': policy['celex_id'],
                'title': policy['title'],
                'similarity': float(similarity)
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def classify_violation(self, text: str) -> Dict:
        """Classify the type of violation"""
        if self.classifier is None:
            return {'error': 'Classifier not loaded'}
        
        model_data = self.classifier
        vectorizer = model_data['vectorizer']
        classifier = model_data['classifier']
        label_encoder = model_data['label_encoder']
        
        # Vectorize
        X = vectorizer.transform([text])
        
        # Predict
        prediction = classifier.predict(X)[0]
        prediction_label = label_encoder.inverse_transform([prediction])[0]
        
        # Get probabilities
        probabilities = classifier.predict_proba(X)[0]
        class_probs = {
            label_encoder.inverse_transform([i])[0]: prob 
            for i, prob in enumerate(probabilities)
        }
        
        return {
            'violation_type': prediction_label,
            'confidence': max(probabilities),
            'all_probabilities': class_probs
        }

# Example usage
if __name__ == "__main__":
    loader = ModelLoader()
    
    test_texts = [
        "This website collects personal data without user consent",
        "Our AI system makes decisions that affect users",
        "All user data is encrypted and protected",
        "The website has no privacy policy"
    ]
    
    for text in test_texts:
        print("\n" + "="*50)
        print(f"Text: {text}")
        
        result = loader.detect_violation(text)
        print(f"Violation: {result.get('category', 'Unknown')}")
        print(f"Confidence: {result.get('confidence', 0):.3f}")
        
        similar = loader.find_similar_policies(text)
        print("Similar policies:")
        for policy in similar[:2]:
            print(f"  - {policy['title']} ({policy['similarity']:.3f})")