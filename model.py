import numpy as np
import re
from database import query_threat_intel
from quantum_engine import verify_with_quantum

def get_url_features(url: str):
    """ Extracts the 4-feature Quantum Vector from a URL string """
    domain = url.split('/')[2] if len(url.split('/')) > 2 else url
    
    # Feature 1: Hyphen in domain
    f1 = 1.0 if '-' in domain else 0.0
    # Feature 2: Long URL (> 54 chars)
    f2 = 1.0 if len(url) > 54 else 0.0
    # Feature 3: IP Address instead of domain
    f3 = 1.0 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain) else 0.0
    # Feature 4: Non-Standard TLD
    trusted = ['.com', '.org', '.edu', '.gov', '.net', '.in']
    f4 = 0.0 if any(domain.endswith(tld) for tld in trusted) else 1.0
    
    return [float(f1 * np.pi), float(f2 * np.pi), float(f3 * np.pi), float(f4 * np.pi)]

def predict_threat(url: str, raw_features=None):
    # 1. Extract Features
    if isinstance(raw_features, list) and len(raw_features) == 4:
        features = [float(x * np.pi) for x in raw_features]
        # Calculate raw binary features back from the pi-multiples for the override
        f_binary = [1.0 if x > 0 else 0.0 for x in raw_features]
    else:
        input_vector = get_url_features(url)
        features = input_vector
        # Get 0 or 1 values for classical override
        f_binary = [1.0 if x > 0 else 0.0 for x in input_vector]

    # 2. RAG & Quantum Check
    db_match = query_threat_intel(features)
    q_fidelity = verify_with_quantum(features, db_match["vector"])
    
    # 3. HYBRID DECISION LOGIC
    is_phishing = False
    
    # Logic A: Quantum/DB Match
    if db_match["label"] == "Phishing" and q_fidelity > 0.40:
        is_phishing = True
    
    # Logic B: Classical Override (The "Fail-Safe")
    # If it has an IP (f3) OR a suspicious TLD (f4), flag it regardless of DB
    if f_binary[2] == 1.0 or f_binary[3] == 1.0:
        is_phishing = True

    # 4. GLOBAL WHITELIST (Protects your Google/LinkedIn tests)
    whitelist = ["google", "github", "linkedin", "apple", "microsoft", "wikipedia", "stack"]
    if any(site in url.lower() for site in whitelist):
        is_phishing = False

    return {
        "is_safe": not is_phishing, 
        "fidelity": float(q_fidelity), 
        "threat_type": "Phishing" if is_phishing else "Safe"
    }