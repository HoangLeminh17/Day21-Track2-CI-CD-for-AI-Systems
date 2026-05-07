from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import botocore
import joblib
import os

app = FastAPI()

CLOUD_BUCKET = os.environ.get("CLOUD_BUCKET")
S3_MODEL_KEY = os.environ.get("S3_MODEL_KEY", "models/latest/model.pkl")
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    """Download model.pkl from S3 to local MODEL_PATH."""
    if not CLOUD_BUCKET:
        print("CLOUD_BUCKET not set, skipping model download")
        return

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    s3 = boto3.client("s3")
    try:
        s3.download_file(CLOUD_BUCKET, S3_MODEL_KEY, MODEL_PATH)
        print(f"Model downloaded from s3://{CLOUD_BUCKET}/{S3_MODEL_KEY} to {MODEL_PATH}")
    except botocore.exceptions.ClientError as e:
        print(f"Could not download model from S3: {e}")


# Try to download model at startup
download_model()

model = None
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Failed to load model: {e}")


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    """Return server health. If model missing, status indicates so."""
    if model is None:
        return {"status": "no_model"}
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not isinstance(req.features, list) or len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")

    try:
        pred = model.predict([req.features])[0]
        label_map = {0: "thấp", 1: "trung_bình", 2: "cao"}
        return {"prediction": int(pred), "label": label_map.get(int(pred), "khong_ro")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
