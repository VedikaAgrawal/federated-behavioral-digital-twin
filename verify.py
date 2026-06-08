from src.fraud_engine import FraudDetector
from src.data_generator import TransactionGenerator
import time

def verify_system():
    print("--- Starting System Verification ---")
    
    # 1. Init Components
    detector = FraudDetector()
    generator = TransactionGenerator()
    
    # 2. specific user
    user = generator.generate_user_profile()
    user_id = user["user_id"]
    print(f"Created User: {user['name']} from {user['home_city']}")
    
    # 3. Feed 5 legitimate transactions (Learning Phase)
    print("\n[Phase 1] Learning Phase (5 Legit Transactions)")
    for i in range(5):
        tx = generator.generate_transaction(user, is_fraud=False)
        tx["user_id"] = user_id
        result = detector.analyze_transaction(tx)
        print(f"Tx {i+1}: ${tx['amount']:.2f} at {tx['city']} -> {result['decision']} (Risk: {result['risk_score']:.2f})")
        
    # 4. Feed 1 Fraud Transaction
    print("\n[Phase 2] Attack Phase (Mixed Tests)")
    
    # Test A: Transfer Scam
    print("--- Test A: Transfer to Unknown Recipient ---")
    fraud_tx = generator.generate_transaction(user, is_fraud=True)
    # Force it to be a transfer scam for the test
    fraud_tx["type"] = "transfer"
    fraud_tx["recipient_id"] = "unknown_hacker_123"
    fraud_tx["category"] = "transfer"
    fraud_tx["user_id"] = user_id
    
    result = detector.analyze_transaction(fraud_tx)
    print(f"Transfer Scam -> {result['decision']} (Risk: {result['risk_score']:.2f})")
    if result['rule_based_reasons']: print(f"Reasons: {result['rule_based_reasons']}")

    # Test B: Sequence Anomaly
    print("\n--- Test B: Sequence Anomaly ---")
    # First, train a pattern: Gas -> Food (3 times)
    print("Training Pattern: 'gas' -> 'dining'...")
    for _ in range(3):
        t1 = generator.generate_transaction(user, is_fraud=False)
        t1["category"] = "gas"
        t1["user_id"] = user_id
        detector.analyze_transaction(t1)
        
        t2 = generator.generate_transaction(user, is_fraud=False)
        t2["category"] = "dining"
        t2["user_id"] = user_id
        detector.analyze_transaction(t2)
        
    # Now break it: Gas -> Electronics
    print("Executing Break: 'gas' -> 'electronics'")
    # Set context to gas
    t_context = generator.generate_transaction(user, is_fraud=False)
    t_context["category"] = "gas"
    t_context["user_id"] = user_id
    detector.analyze_transaction(t_context)
    
    # abnormal follow-up
    t_break = generator.generate_transaction(user, is_fraud=False)
    t_break["category"] = "electronics"
    t_break["user_id"] = user_id
    
    result = detector.analyze_transaction(t_break)
    
    print(f"Sequence Break -> {result['decision']} (Risk: {result['risk_score']:.2f})")
    if result['rule_based_reasons']:
        print(f"Reasons: {result['rule_based_reasons']}")
        
    if result['decision'] in ["DECLINED", "REVIEW"]:
        print("SUCCESS: System caught the anomaly.")
    else:
        print("WARNING: System missed the anomaly (might need more training data).")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_system()
