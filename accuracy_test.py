import requests

API_URL = "http://127.0.0.1:8000/scan"

# --- EXPANDED TEST DATASET (20 URLs) ---
test_data = [
    # Safe / Whitelisted
    ("https://google.com", True),
    ("https://github.com", True),
    ("https://apple.com", True),
    ("https://microsoft.com", True),
    ("https://stackoverflow.com", True),
    ("https://linkedin.com", True),
    ("https://flutter.dev", True),
    ("https://python.org", True),
    ("https://aws.amazon.com", True),
    ("https://wikipedia.org", True),
    
    # Phishing / Malicious
    ("http://123.45.67.89/login-secure", False),
    ("http://paypal-verification-update.com", False),
    ("http://secure-amazon-account-check.xyz", False),
    ("http://login.microsoftonline.security-verify.net", False),
    ("http://bank-of-america-portal.com", False),
    ("http://bit.ly/fake-login-123", False),
    ("http://wellsfargo-secure-auth.org", False),
    ("http://netflix-payment-update.shop", False),
    ("http://facebook-login-help.xyz", False),
    ("http://192.168.1.1/admin/login.php", False)
]

def run_expanded_test():
    print(f"🚀 Initializing Q-Shield Stress Test (N={len(test_data)})...")
    print("-" * 60)
    
    correct = 0
    
    for url, expected_safe in test_data:
        try:
            response = requests.post(API_URL, json={"url": url})
            data = response.json()
            
            actual_safe = data['is_safe']
            conf = data['quantum_confidence']
            
            is_correct = (actual_safe == expected_safe)
            if is_correct: correct += 1
            
            status = "✅" if is_correct else "❌"
            label = "SAFE" if actual_safe else "PHISH"
            print(f"{status} [{label}] {url[:45]}... (Conf: {conf})")
            
        except Exception as e:
            print(f"⚠️ Error testing {url}: {e}")

    accuracy = (correct / len(test_data)) * 100
    print("-" * 60)
    print(f"📊 FINAL STRESS TEST ACCURACY: {accuracy:.2f}%")
    print(f"✅ Pass: {correct} | ❌ Fail: {len(test_data) - correct}")
    print("-" * 60)

if __name__ == "__main__":
    run_expanded_test()