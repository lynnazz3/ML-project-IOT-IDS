# ML-project-IOT-IDS
IoT Intrusion Detection System — LightGBM + Differential Evolution + FastAPI + Docker

# Workflow Summary
Preprocessing: Raw network packets are converted into numerical features (e.g., packet length, flow duration).

Optimization: The Differential Evolution algorithm finds the best configurations for the LightGBM classifier.

Training: The model is trained on labeled IoT attack data.

Integration: The model is serialized (e.g., as a .pkl or .joblib file) and loaded into a FastAPI application.

Containerization: A Dockerfile builds an image that serves the model, ready for orchestration.
