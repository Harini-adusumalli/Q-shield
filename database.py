import os
import pandas as pd
import requests
import chromadb
import numpy as np

# --- CONFIGURATION ---
DATA_PATH = "phishing_data.csv"
DATA_URL = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"

# Persistent client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
# Using a NEW collection name 'v2' to bypass the locked old data
collection = chroma_client.get_or_create_collection(name="v2_power_features")

def initialize_database():
    # 1. Download if missing
    if not os.path.exists(DATA_PATH):
        print("📥 CSV missing. Downloading from GitHub...")
        response = requests.get(DATA_URL)
        with open(DATA_PATH, 'wb') as f:
            f.write(response.content)
        print("✅ Download complete.")

    # 2. Only seed if this specific collection is empty
    if collection.count() > 0:
        print(f"📦 Collection 'v2' already has {collection.count()} signatures.")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Power Features based on your CSV columns
    feature_cols = ['Prefix/Suffix', 'URL_Length', 'Have_IP', 'Web_Traffic']
    
    # Check if columns exist (sometimes GitHub headers change)
    if not all(col in df.columns for col in feature_cols):
        print(f"⚠️ Column mismatch. CSV has: {df.columns.tolist()[:5]}")
        # Fallback to first 4 numeric columns if naming is weird
        feature_cols = df.select_dtypes(include=[np.number]).columns[1:5]

    labels = df.iloc[:, -1].values 

    print(f"⚛️  Seeding V2 with: {list(feature_cols)}")
    
    sample_size = min(300, len(df))
    sample_indices = np.random.choice(len(df), sample_size, replace=False)
    
    for i in sample_indices:
        raw_vector = df.loc[i, feature_cols].astype(float).tolist()
        # Scale by PI for the Quantum Engine
        vector = [float(x * np.pi) for x in raw_vector]
        
        label_text = "Phishing" if str(labels[i]) == "1" else "Safe"
        collection.add(
            embeddings=[vector], 
            documents=[label_text], 
            ids=[f"id_v2_{i}"]
        )

    print(f"✅ DB V2 Ready. Total: {collection.count()}")

def query_threat_intel(input_vector):
    results = collection.query(
        query_embeddings=[input_vector], 
        n_results=1, 
        include=['embeddings', 'documents']
    )
    if not results['embeddings'] or len(results['embeddings'][0]) == 0:
        return {"label": "Safe", "vector": [0.0]*4}
    return {
        "label": results['documents'][0][0], 
        "vector": results['embeddings'][0][0]
    }

if __name__ == "__main__":
    initialize_database()