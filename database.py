import os
import pandas as pd
import chromadb
import numpy as np

DATA_PATH = "phishing_data.csv"
chroma_client = chromadb.PersistentClient(path="./chroma_db")
# Using a fresh collection name to ensure no old data interference
collection = chroma_client.get_or_create_collection(name="q_shield_v3")

def initialize_database():
    if collection.count() >= 3000:
        print(f"📦 Database already has {collection.count()} signatures. Ready for demo.")
        return

    if not os.path.exists(DATA_PATH):
        print("❌ Error: phishing_data.csv not found!")
        return

    df = pd.read_csv(DATA_PATH)
    train_df = df.head(3000) 
    
    # We use these 4 specific columns as our "Quantum DNA"
    feature_cols = ['Prefix/Suffix', 'URL_Length', 'Have_IP', 'Web_Traffic']
    
    print(f"⚛️  Seeding Q-Shield Knowledge Base with 3,000 signatures...")

    for i, row in train_df.iterrows():
        # Classical to Quantum Mapping
        f1, f2, f3, f4 = row[feature_cols].astype(float).tolist()
        vector = [float(f1 * np.pi), float(f2 * np.pi), float(f3 * np.pi), float(f4 * np.pi)]
        
        # Label 1 = Phishing, Label 0 = Safe
        label_text = "Phishing" if str(row['Label']) == "1" else "Safe"
        
        collection.add(
            embeddings=[vector], 
            documents=[label_text], 
            ids=[f"id_{i}"]
        )

    print(f"✅ DB Ready. Total Signatures: {collection.count()}")
def query_threat_intel(input_vector):
    # Search for the top 10 nearest neighbors
    results = collection.query(
        query_embeddings=[input_vector], 
        n_results=10, 
        include=['embeddings', 'documents']
    )
    
    if not results['documents'] or len(results['documents'][0]) == 0:
        return {"label": "Safe", "vector": [0.0]*4}

    # SEARCH LOGIC: If any of the 10 neighbors are Phishing, 
    # we return that Phishing vector to see if the user's URL matches its structure.
    docs = results['documents'][0]
    embs = results['embeddings'][0]
    
    for idx, label in enumerate(docs):
        if label == "Phishing":
            return {"label": "Phishing", "vector": embs[idx]}
            
    # If all 10 neighbors are Safe, return the closest Safe match
    return {"label": "Safe", "vector": embs[0]}
if __name__ == "__main__":
    initialize_database()