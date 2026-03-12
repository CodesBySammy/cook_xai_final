import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "my_super_secure_webhook_secret_123")
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    MODEL_PATH = os.path.join(MODELS_DIR, "jit_risk_model.pkl")

settings = Settings()