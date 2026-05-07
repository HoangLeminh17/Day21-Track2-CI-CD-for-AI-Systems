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
    except botocore.exceptions.ClientError as exc:
        print(f"Could not download model from S3: {exc}")


download_model()

model = None
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as exc:
        print(f"Failed to load model: {exc}")


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")

    try:
        pred = int(model.predict([req.features])[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    label_map = {0: "thap", 1: "trung_binh", 2: "cao"}
    return {"prediction": pred, "label": label_map.get(pred, "khong_ro")}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
