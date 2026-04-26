# To run locally: pip install fastapi uvicorn, then: uvicorn script:app --reload
from fastapi import FastAPI
import numpy as np
import joblib

app = FastAPI()


model         = joblib.load('models/iot_model.pkl')
scaler        = joblib.load('models/scaler.pkl')
imputer       = joblib.load('models/imputer.pkl')
label_encoder = joblib.load('models/label_encoder.pkl')
thresholds    = joblib.load('models/thresholds.pkl')

@app.post("/predict")
def predict(features: list):
    x = np.array(features).reshape(1, -1)
    x = imputer.transform(x)
    x = scaler.transform(x)

    probs = model.predict(x)
    pred  = np.argmax(probs / thresholds, axis=1)[0]

    return {
        "prediction": encoder.classes_[pred],
        "confidence": float(probs[0, pred])
    }
