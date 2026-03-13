import numpy as np
from database import query_threat_intel
from quantum_engine import verify_with_quantum

def get_url_features(url: str):
    # f1: Prefix/Suffix (Hyphen in domain)
    domain = url.split('/')[2] if len(url.split('/')) > 2 else ""
    f1 = 1.0 if '-' in domain else 0.0
    
    # f2: URL_Length (Dataset threshold is usually 54)
    f2 = 1.0 if len(url) > 54 else 0.0
    
    # f3: Have_IP
    import re
    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    f3 = 1.0 if ip_pattern.match(domain) else 0.0
    
    # f4: Web_Traffic (Proxy: 0 for trusted TLDs, 1 for suspicious)
    trusted_tlds = ['.com', '.org', '.edu', '.gov', '.net']
    f4 = 0.0 if any(domain.endswith(tld) for tld in trusted_tlds) else 1.0
    
    # MULTIPLY BY PI to rotate into the same Hilbert Space
    return [float(x * np.pi) for x in [f1, f2, f3, f4]]
def predict_threat(url: str, raw_features=None):
    # If we have raw features from the CSV, use them. Otherwise, extract from URL.
    if raw_features:
        input_vector = [float(x * np.pi) for x in raw_features]
    else:
        input_vector = get_url_features(url)
        
    db_match = query_threat_intel(input_vector)
    q_fidelity = verify_with_quantum(input_vector, db_match["vector"])
    
    is_phishing = False
    
    # Logic: Trust the RAG + Quantum overlap
    if db_match["label"] == "Phishing" and q_fidelity > 0.05:
        is_phishing = True
        
    # Whitelist still applies for safety
    whitelist = ["google", "apple", "github"]
    if any(d in url.lower() for d in whitelist) and url.startswith("https"):
        is_phishing = False

    return {"is_safe": not is_phishing, "fidelity": q_fidelity}