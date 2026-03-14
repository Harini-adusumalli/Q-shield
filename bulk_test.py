import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000/scan"

def run_bulk_validation(n=100): 
    print(f"🚀 Starting Hybrid Bulk Validation (N={n})...")
    df = pd.read_csv("phishing_data.csv")
    test_pool = df.iloc[3000:] # Testing on data NOT in the DB
    sample_df = test_pool.sample(n)
    
    feature_cols = ['Prefix/Suffix', 'URL_Length', 'Have_IP', 'Web_Traffic']
    correct = 0
    for i, (_, row) in enumerate(sample_df.iterrows()):
        expected_safe = True if str(row['Label']) == "0" else False
        payload = {"url": row['Domain'], "raw_features": row[feature_cols].astype(float).tolist()}
        
        try:
            res = requests.post(API_URL, json=payload)
            actual_safe = res.json()['is_safe']
            if actual_safe == expected_safe:
                correct += 1
            if i % 10 == 0: print(f"Processing... {i}/{n}")
        except Exception as e:
            print(f"Error: {e}")

    print("-" * 30)
    print(f"📊 FINAL BULK ACCURACY (Unseen Data): {(correct/n)*100:.2f}%")
    print("-" * 30)

if __name__ == "__main__":
    run_bulk_validation(100)