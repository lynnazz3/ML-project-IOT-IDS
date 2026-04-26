# IoT Intrusion Detection System
### Streaming ML Pipeline with Drift Monitoring

A machine learning-based Intrusion Detection System (IDS) for IoT network 
traffic. Classifies network flows into 8 categories — Benign, DDoS, DoS, 
Mirai, Recon, Spoofing, BruteForce, and Web_Based — using LightGBM with 
Differential Evolution threshold optimisation.

**Test Set Macro-F1: 0.664 | DDoS F1: 0.891 | False Positive Rate: 12.8%**

---

## Table of Contents

- [Project Overview](#project-overview)
- [Dataset](#dataset)
- [Results](#results)
- [Project Structure](#project-structure)
- [Quick Start with Docker](#quick-start-with-docker)
- [Run Locally](#run-locally)
- [API Usage](#api-usage)
- [Pipeline Overview](#pipeline-overview)
- [Requirements](#requirements)

---

## Project Overview

This project addresses three core challenges in IoT intrusion detection:

1. **Severe class imbalance** — DDoS outnumbers BruteForce by 2,521:1
2. **Rare attack detection** — BruteForce and Web_Based have fewer than 
   300 real training examples each
3. **Production readiness** — the system includes drift monitoring and 
   a real-time inference API

Key design decisions:
- **Macro-F1** as the primary metric — gives equal weight to all 8 classes 
  regardless of frequency. Accuracy is misleading here because a model 
  predicting DDoS every time scores 72% while missing every rare attack.
- **Two-stage balancing** — caps dominant classes at 80,000 and lifts 
  minorities to 15,000 using RandomOverSampler
- **Differential Evolution threshold optimisation** — finds 8 per-class 
  decision thresholds simultaneously to stop dominant classes suppressing 
  rare ones
- **Drift monitoring** — three mechanisms detect when live traffic diverges 
  from training distribution

---

## Dataset

**Full Dataset — CICIoT2023**
Download the full 712,300-flow dataset from:
https://www.unb.ca/cic/datasets/iotdataset-2023.html

Place it at the project root as `Merged01.csv` to retrain the model.

**Sample Data — sampledata.csv**
A representative subset of the dataset is included in the repository.
This can be used to test the pipeline and API without downloading
the full dataset. Note that model performance on the sample will
differ from the full dataset results reported above.


## Results

### Test Set Performance (unseen data, touched once)

| Model | Macro-F1 | Accuracy | FPR-Benign |
|-------|----------|----------|------------|
| Logistic Regression | 0.247 | 48.8% | 65.5% |
| HistGradientBoosting | 0.644 | 74.6% | 18.6% |
| **LightGBM + DE Thresholds** | **0.664** | **83.5%** | **12.8%** |

### Per-Class F1 — LightGBM + DE Thresholds

| Class | F1 | Notes |
|-------|----|-------|
| Mirai | 1.000 | Highly distinctive traffic signature |
| DDoS | 0.891 | Strong volumetric detection |
| Spoofing | 0.850 | ARP/DNS spoofing patterns clear |
| Benign | 0.830 | Low false alarm rate |
| Recon | 0.710 | Port scan patterns learnable |
| DoS | 0.590 | DDoS/DoS flow overlap reduces precision |
| BruteForce | 0.302 | Only 31 test examples — data limited |
| Web_Based | 0.136 | Flow features cannot see HTTP payload |

---

## Project Structure
ML-project-IOT-IDS
├── MlProjectfinall.ipynb   # Full training pipeline notebook 
├── sampledata.csv                # Sample subset of CICIoT2023 dataset
│
├── models/                          # All inference artifacts in one file
│   └── imputer.pkl 
│   └── iot_model.pkl
│   └── label_encoder.pkl    
│   └── scaler.pkl          
│   └── thresholds.pkl                       
│
├── app.py  # FastAPI inference endpoint
│                 
│
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
└── README.md                    # This file


## Model Artifacts

The trained model artifacts exceed GitHub's 100MB file size limit.

Download here:
[iot_ids_artifacts.pkl](https://drive.google.com/drive/folders/1D2yKbg0StC5awN_waoHn2VQXAQ4DVbOz?usp=drive_link)

After downloading place the file at:
ML-project-IOT-IDS/models/iot_ids_artifacts.pkl



---

## Quick Start with Docker

### Pull and Run the Pre-built Image

docker pull nn33/intrusion-detection-app:latest
docker run -p 8000:8000 nn33/intrusion-detection-app:latest

The API is now running at http://localhost:8000

Test it:
curl http://localhost:8000/health

### Build the Image Yourself

git clone https://github.com/lynnazz3/ML-project-IOT-IDS.git
cd ML-project-IOT-IDS
docker build -t nn33/intrusion-detection-app .
docker run -p 8000:8000 nn33/intrusion-detection-app

---

## Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/lynnazz3/ML-project-IOT-IDS.git
cd ML-project-IOT-IDS

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Dataset

**Sample Data**
A representative subset is available on Google Drive:
[sampledata.csv](https://drive.google.com/file/d/1rz7RL4mZJqppUeU4fXmc9m3Csv5OZ73z/view?usp=drive_link)

After downloading place it at the project root:
ML-project-IOT-IDS/sampledata.csv

To retrain on the full dataset, download the
CICIoT2023 dataset page and place it in the project root.

### 4. Run the Notebook

Open MlProjectfinall.ipynb in Jupyter or Google Colab and run all cells 
top to bottom. This will:
- Load and preprocess the data
- Engineer 13 domain features
- Train LR, HistGBM, and LightGBM models
- Run Differential Evolution threshold optimisation
- Evaluate on the test set
- Save all artifacts to saved_models/

### 5. Start the API

```bash
uvicorn app.main:app --reload --port 8000
```

---

## API Usage

### Endpoint


### Request Body

Send a JSON object with the 52 feature values of one network flow:

```json
{
  "Header_Length": 20.0,
  "Protocol_Type": 6.0,
  "Time_To_Live": 64.0,
  "Rate": 15000.0,
  "fin_flag_number": 0.0,
  "syn_flag_number": 1.0,
  "rst_flag_number": 0.0,
  "psh_flag_number": 0.0,
  "ack_flag_number": 0.0,
  "ack_count": 0.0,
  "syn_count": 100.0,
  "fin_count": 0.0,
  "rst_count": 0.0,
  "...": "all 52 features required"
}
```

### Response

```json
{
  "prediction": "DDoS",
  "confidence": 0.8821,
  "all_probabilities": {
    "Benign": 0.0312,
    "BruteForce": 0.0011,
    "DDoS": 0.8821,
    "DoS": 0.0743,
    "Mirai": 0.0089,
    "Recon": 0.0014,
    "Spoofing": 0.0007,
    "Web_Based": 0.0003
  }
}
```

### Health Check

```bash
GET /health
```

Returns:
```json
{
  "status": "ok",
  "model": "LightGBM + DE Thresholds",
  "classes": 8,
  "features": 52
}
```

---

## Pipeline Overview
Raw CSV (712,300 flows)
↓
Load + validate (drop nulls, replace inf)
↓
Label mapping (34 attack types → 8 categories)
↓
Feature engineering (39 raw → 52 features)
↓
Stratified 70/15/15 split
↓
Median imputation + RobustScaler
(fitted on training data only — no leakage)
↓
Two-stage balancing
Stage 1: Cap DDoS/DoS at 80,000
Stage 2: ROS lifts minorities to 15,000
(applied only to training set)
↓
LightGBM training

Per-sample class weights
Logloss early stopping
52 features, 8 classes
↓
Differential Evolution threshold optimisation
8 thresholds optimised simultaneously
Maximises macro-F1 on validation set
↓
Final evaluation on test set (touched once)
↓
Save all artifacts → Deploy via FastAPI + Docker


---

## Requirements
python>=3.9
lightgbm>=3.3.0
scikit-learn>=1.0.0
imbalanced-learn>=0.9.0
polars>=0.16.0
pandas>=1.4.0
numpy>=1.21.0
fastapi>=0.85.0
uvicorn>=0.18.0
scipy>=1.7.0
joblib>=1.1.0

Install all at once:
```bash
pip install -r requirements.txt
```

---

## Key Design Notes

**Why Macro-F1 over Accuracy**  
With 72% DDoS traffic, accuracy rewards predicting DDoS every time. 
Macro-F1 gives equal weight to all 8 classes — a model that ignores 
BruteForce gets the same penalty as one that ignores DDoS.

**Why Two-Stage Balancing over SMOTE**  
With only 143 real BruteForce examples, SMOTE interpolates between 
points in an extremely small cluster — generating near-duplicates, 
not genuine diversity. Two-stage ROS with dominant class capping 
fixes the ratio problem without synthesising data we cannot validate.

**Why Differential Evolution over Per-Class Threshold Sweep**  
Lowering BruteForce's threshold steals probability space from DDoS. 
A per-class sweep treats thresholds as independent — DE optimises 
all 8 simultaneously, capturing those interactions.

**Why the Artifacts Are Saved Together**  
The imputer, scaler, model, thresholds, and label encoder must all 
match the training pipeline exactly. Saving them as one file prevents 
any component from being updated independently and breaking inference.

---

## Drift Monitoring

Three monitors run alongside predictions in production:

- **KS-Test** — Kolmogorov-Smirnov test per feature comparing 
  incoming distribution against training reference. p < 0.01 triggers alert.
- **Rolling Alert Rate** — fraction of flows predicted as attacks 
  over a 1,000-flow window. Sudden spikes trigger investigation.
- **DDoS Rate Monitor** — DDoS fraction per 500-flow window. 
  Shift greater than 20% between windows triggers alert.

---

*CICIoT2023 dataset: https://www.unb.ca/cic/datasets/iotdataset-2023.html*  
*Reference paper: https://www.mdpi.com/1424-8220/23/13/5941*

