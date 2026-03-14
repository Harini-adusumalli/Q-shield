import os
import pandas as pd
import chromadb
import numpy as np

DATA_PATH = "phishing_data.csv"
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="v2_power_features")

def initialize_database():
    # Force a clean seed for the hackathon
    if collection.count() > 0:
        print(f"📦 DB already seeded. Delete 'chroma_db' folder for a fresh start.")
        return

    df = pd.read_csv(DATA_PATH)
    # Seed Knowledge Base with first 3000 rows
    train_df = df.head(3000) 
    feature_cols = ['Prefix/Suffix', 'URL_Length', 'Have_IP', 'Web_Traffic']
    
    print(f"⚛️  Seeding Knowledge Base (0=Safe, 1=Phishing)...")

    for i, row in train_df.iterrows():
        f1, f2, f3, f4 = row[feature_cols].astype(float).tolist()
        vector = [float(f1 * np.pi), float(f2 * np.pi), float(f3 * np.pi), float(f4 * np.pi)]
        
        # KEY FIX: Match the CSV Labels precisely
        label_text = "Phishing" if str(row['Label']) == "1" else "Safe"
        
        collection.add(embeddings=[vector], documents=[label_text], ids=[f"id_train_{i}"])

    print(f"✅ DB Seeded with {collection.count()} signatures.")

def query_threat_intel(input_vector):
    results = collection.query(query_embeddings=[input_vector], n_results=1, include=['embeddings', 'documents'])
    if not results['embeddings'] or len(results['embeddings'][0]) == 0:
        return {"label": "Safe", "vector": [0.0]*4}
    return {"label": results['documents'][0][0], "vector": results['embeddings'][0][0]}

if __name__ == "__main__":
    initialize_database()