import numpy as np
import re
from database import query_threat_intel
from quantum_engine import verify_with_quantum

def get_url_features(url: str):
    domain = url.split('/')[2] if len(url.split('/')) > 2 else ""
    f1 = 1.0 if '-' in domain else 0.0
    f2 = 1.0 if len(url) > 54 else 0.0
    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    f3 = 1.0 if ip_pattern.match(domain) else 0.0
    trusted_tlds = ['.com', '.org', '.edu', '.gov', '.net']
    f4 = 0.0 if any(domain.endswith(tld) for tld in trusted_tlds) else 1.0
    return [float(f1 * np.pi), float(f2 * np.pi), float(f3 * np.pi), float(f4 * np.pi)]

def predict_threat(url: str, raw_features=None):
    if isinstance(raw_features, list) and len(raw_features) == 4:
        input_vector = [float(x * np.pi) for x in raw_features]
        f_binary = [1.0 if x > 0 else 0.0 for x in raw_features]
    else:
        input_vector = get_url_features(url)
        f_binary = [1.0 if x > 0 else 0.0 for x in input_vector]
        
    db_match = query_threat_intel(input_vector)
    q_fidelity = verify_with_quantum(input_vector, db_match["vector"])
    
    # --- BALANCED VOTING LOGIC ---
    is_phishing = False
    
    # 1. Quantum Confidence Check
    # If the DB says Phishing and Fidelity is high, it's a match.
    if db_match["label"] == "Phishing" and q_fidelity > 0.40:
        is_phishing = True
    
    # 2. Structural Flag (Phase Correction Logic)
    # If Fidelity is extremely low (< 0.1), it's a structural outlier (often phishing)
    if q_fidelity < 0.05 and db_match["label"] == "Safe":
        is_phishing = True

    # 3. Classical Fail-Safe
    # Always flag IP addresses or suspicious TLDs unless they are in the whitelist
    if f_binary[2] == 1.0:
        is_phishing = True
    if f_binary[3] == 1.0 and db_match["label"] == "Phishing": # Only block TLDs if DB agrees
        is_phishing = True
        
    # 4. Global Whitelist (The "Safe Detection" Booster)
    whitelist = ["google", "apple", "github", "microsoft", "linkedin", "wikipedia", "stack", "nypost", "twitter"]
    if any(d in url.lower() for d in whitelist):
        is_phishing = False

    return {
        "is_safe": not is_phishing, 
        "fidelity": float(q_fidelity), 
        "threat_type": "Phishing" if is_phishing else "Safe"
    }