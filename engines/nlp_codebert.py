from transformers import pipeline
from core.logger import logger

class NLPCodeBERT:
    def __init__(self):
        logger.info("Loading CodeBERT (May take a moment)...")
        try:
            self.analyzer = pipeline("text-classification", model="mrm8488/codebert-base-finetuned-detect-insecure-code")
            logger.info("✅ CodeBERT Initialized.")
        except Exception as e:
            logger.error(f"CodeBERT load failed: {e}")
            self.analyzer = None

    def scan(self, raw_code: str, filename: str) -> str:
        if not self.analyzer: return ""
        try:
            prediction = self.analyzer(raw_code[:1500])
            label = prediction[0]['label']
            confidence = round(prediction[0]['score'] * 100, 2)
            
            if label in ["VULNERABLE", "LABEL_1"]:
                return f"* 🔴 **Security (`{filename}`)**: Semantic vulnerability detected ({confidence}% confidence)."
            return f"* 🟢 **Security (`{filename}`)**: Logic appears secure."
        except Exception:
            return ""

nlp_engine = NLPCodeBERT()