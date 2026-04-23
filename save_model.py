import os
import joblib
from matcher import load_tenders, build_tfidf_index

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
os.makedirs(MODEL_DIR, exist_ok=True)

tenders = load_tenders()
vectorizer, _ = build_tfidf_index(tenders)

output_path = os.path.join(MODEL_DIR, "vectorizer.joblib")
joblib.dump(vectorizer, output_path)
print("Model saved to model/vectorizer.joblib")
