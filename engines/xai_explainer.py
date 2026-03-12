import joblib
import pandas as pd
import numpy as np
import shap
from core.config import settings
from core.logger import logger

class XAIExplainer:
    def __init__(self):
        try:
            self.model = joblib.load(settings.MODEL_PATH)
            self.explainer = shap.TreeExplainer(self.model)
            logger.info("XAI Engine & SHAP loaded successfully.")
        except Exception as e:
            logger.warning(f"XAI Engine unavailable (Train model first): {e}")
            self.model = None

    def analyze_risk(self, la: int, ld: int, nf: int) -> tuple:
        if not self.model:
            return 0.0, "⚠️ ML Model missing. Run `python pipelines/train_rf_model.py`."

        df = pd.DataFrame([{"la": la, "ld": ld, "nf": nf}])
        
        # Get probability of risk (Class 1)
        risk_prob = self.model.predict_proba(df)[0][1] * 100
        
        # SHAP Values
        shap_values = self.explainer.shap_values(df)
        
        # Safely handle different SHAP library versions
        if isinstance(shap_values, list):
            sv = shap_values[1][0]  # Older SHAP: List format
        elif len(np.array(shap_values).shape) == 3:
            sv = shap_values[0, :, 1]  # Newer SHAP: 3D Array format
        else:
            sv = shap_values[0]  # Fallback

        report = f"### 🧠 Explainable AI Deployment Risk\n**Risk Score: {risk_prob:.2f}%**\n\n"
        report += "How the AI calculated this based on PR architecture:\n"
        
        features = ["Lines Added (la)", "Lines Deleted (ld)", "Number of Files (nf)"]
        for i, feature in enumerate(features):
            # Ensure impact is forced into a standard Python float
            impact = float(sv[i]) * 100
            direction = "increased 🔺" if impact > 0 else "decreased 📉"
            report += f"* `{feature}`: {direction} risk by {abs(impact):.2f}%\n"

        return risk_prob, report

xai_engine = XAIExplainer()