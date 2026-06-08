try:
    from .digital_twin import DigitalTwin
except (ImportError, ValueError):
    from digital_twin import DigitalTwin
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from .bfl_ledger import BlockchainLedger
except (ImportError, ValueError):
    from bfl_ledger import BlockchainLedger

class FraudDetector:
    def __init__(self, bank_id="SBI_INDIA"):
        self.bank_id = bank_id
        self.twins = {} # user_id -> DigitalTwin
        self.ledger = BlockchainLedger()
        self.bfl_enabled = True

    def get_or_create_twin(self, user_id):
        if user_id not in self.twins:
            self.twins[user_id] = DigitalTwin(user_id)
        return self.twins[user_id]

    def analyze_transaction(self, transaction):
        """
        Main entry point with BFL support.
        """
        user_id = transaction.get("user_id", "unknown")
        twin = self.get_or_create_twin(user_id)
        
        # Step 1: Get Global Knowledge (BFL / Federated Learning)
        global_wisdom = None
        if self.bfl_enabled:
            global_wisdom = self.ledger.get_global_wisdom()

        # Step 2: Statistical Check (Digital Twin + Global Brain)
        risk_score, risk_reasons = twin.evaluate(transaction, global_weights=global_wisdom)
        
        decision = "APPROVED"
        
        # Step 3: Decision Logic (Tuned for Gold Standard Accuracy)
        if risk_score > 0.85:
            decision = "DECLINED"
            # Federated Learning Simulation
            if transaction.get("is_fraud_ground_truth"):
                self.publish_knowledge(transaction)
        elif risk_score > 0.6: # Increased from 0.35 to reduce False Alarms
            decision = "REVIEW"
        else:
            decision = "APPROVED"
            twin.update_state(transaction)

        return {
            "transaction_id": transaction.get("transaction_id"),
            "risk_score": round(risk_score, 2),
            "rule_based_reasons": risk_reasons,
            "decision": decision,
            "bank_id": self.bank_id
        }


    def publish_knowledge(self, transaction):
        """
        Publishes ONLY anonymized behavioral weights to the Blockchain Ledger.
        This is PURE Federated Learning: No merchant or city names are shared.
        """
        # Calculate behavioral weights (Anonymized parameters)
        # Threshold increased to ₹15,000 for industry-level trends
        model_weights = {
            "high_amount_trend": 0.8 if transaction.get("amount", 0) > 10000 else 0.1,
            "unusual_time_trend": 0.8 if transaction.get("is_night_txn", False) else 0.2,
            "velocity_risk": 0.5
        }
        
        self.ledger.publish_block(
            bank_id=self.bank_id,
            model_weights=model_weights
        )

    def batch_train_local(self, df_history):
        """Trains the Digital Twin using a batch of historical transactions."""
        user_id = df_history.iloc[0]["user_id"]
        twin = self.get_or_create_twin(user_id)
        
        # Convert df rows to transactions and update twin state
        for _, row in df_history.iterrows():
            tx = row.to_dict()
            # Clean up types if needed (df might store strings)
            twin.update_state(tx)
        return len(df_history)

    def batch_train_global(self, df_fraud):
        """Pre-loads the blockchain ledger with shared federated weights (Simulated)."""
        for _, row in df_fraud.iterrows():
            # In Pure Federated Learning, we ignore specific merchant/city columns
            # and only load the behavior weights.
            model_weights = {
                "high_amount_trend": 0.4,   # Reduced from 0.7 to avoid false alarms in simulation
                "unusual_time_trend": 0.8,
                "velocity_risk": 0.6
            }
            self.ledger.publish_block(bank_id=row["bank_id"], model_weights=model_weights)
        return len(df_fraud)


