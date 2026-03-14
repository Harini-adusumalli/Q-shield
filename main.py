import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from model import predict_threat

# Initialize FastAPI app
app = FastAPI(title="Q-Shield: Quantum-Hybrid Threat Detection")

# Define the data structure for incoming requests
class ScanRequest(BaseModel):
    url: str
    # raw_features is optional; used by bulk_test.py for 90%+ accuracy validation
    raw_features: Optional[List[float]] = None

@app.get("/")
async def root():
    return {"message": "Q-Shield Quantum Backend is Online"}

@app.post("/scan")
async def scan_url(request: ScanRequest):
    """
    Main endpoint that orchestrates the Hybrid Quantum-Classical analysis.
    """
    try:
        # Pass both the URL and any raw features provided to the prediction model
        result = predict_threat(request.url, raw_features=request.raw_features)
        
        # We multiply fidelity by 100 to show a readable 'Confidence' percentage
        confidence_pct = round(result["fidelity"] * 100, 2)
        
        return {
            "url": request.url,
            "is_safe": result["is_safe"],
            "quantum_confidence": f"{confidence_pct}%",
            # FIX: Change "label" to "threat_type" to match model.py
            "detected_label": result.get("threat_type", "Unknown"),
            "status": "Success"
        }
    except Exception as e:
        return {"status": "Error", "message": str(e)}
# This block ensures the server starts and STAYS running
if __name__ == "__main__":
    print("🚀 Q-Shield Server Initializing...")
    print("🔗 Point your Flutter app or Bulk Test to http://127.0.0.1:8000/scan")
    uvicorn.run(app, host="127.0.0.1", port=8000)