import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/scan"

# 1. Define our test set (10 Safe, 10 Phishing)
test_urls = [
    # LEGITIMATE SITES
    "https://google.com", "https://github.com", "https://linkedin.com", 
    "https://stackoverflow.com", "https://apple.com", "https://microsoft.com",
    "https://twitter.com", "https://nypost.com", "https://icicibank.com", "https://wikipedia.org",
    
    # SUSPICIOUS / PHISHING PATTERNS
    "http://secure-login-amazon.com/verify", "http://123.45.67.89/login-secure",
    "http://paypal-verification-update.com", "http://secure-amazon-account-check.xyz",
    "http://bank-of-america-login-portal.com", "http://verify-bank-account-update.top",
    "http://kienthuc.net.vn/news/update", "http://login-microsoft-security.net",
    "http://secure-dropbox-share.info", "http://validation-needed-now.biz"
]

def run_automated_demo():
    print(f"🚀 Q-SHIELD BATCH TEST: Running {len(test_urls)} scans...\n")
    print(f"{'URL':<45} | {'SAFE?':<6} | {'CONFIDENCE':<10} | {'LABEL'}")
    print("-" * 80)

    for url in test_urls:
        try:
            # We do NOT send raw_features so the backend uses its logic
            payload = {"url": url}
            res = requests.post(API_URL, json=payload).json()
            
            is_safe = "YES" if res.get('is_safe') else "NO"
            conf = res.get('quantum_confidence', '0.0%')
            label = res.get('detected_label', 'Unknown')
            
            # Truncate long URLs for the table
            display_url = (url[:42] + '..') if len(url) > 44 else url
            print(f"{display_url:<45} | {is_safe:<6} | {conf:<10} | {label}")
            
        except Exception as e:
            print(f"Error scanning {url}: {e}")

if __name__ == "__main__":
    run_automated_demo()