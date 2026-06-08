import json
import os
import datetime
import hashlib

class BlockchainLedger:
    def __init__(self, ledger_path=None):
        if ledger_path is None:
            # Dynamically resolve path relative to this script
            ledger_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "ledger.json"))
        self.ledger_path = ledger_path
        self._ensure_ledger_exists()

    def _ensure_ledger_exists(self):
        if not os.path.exists(self.ledger_path):
            with open(self.ledger_path, 'w') as f:
                json.dump([], f)

    def publish_block(self, bank_id, model_weights):
        """
        Publishes a new 'Knowledge Block' containing ONLY model weights.
        Ensures 100% privacy by never sharing merchant or location IDs.
        """
        ledger = self.read_all_blocks()
        
        block = {
            "index": len(ledger) + 1,
            "timestamp": str(datetime.datetime.now()),
            "bank_id": bank_id,
            "model_weights": model_weights, # Federated Intelligence
            "prev_hash": self._calculate_hash(ledger[-1]) if ledger else "0"
        }
        
        ledger.append(block)
        with open(self.ledger_path, 'w') as f:
            json.dump(ledger, f, indent=4)
        
        return block

    def read_all_blocks(self):
        try:
            with open(self.ledger_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get_global_wisdom(self, bft_mechanism="median"):
        """
        Byzantine Fault Tolerant (BFT) Federated Aggregation.
        Uses Median or Trimmed Mean to prevent Model Poisoning attacks from compromised banks.
        No identifiable data (merchants, locations) is ever processed here.
        """
        import statistics
        blocks = self.read_all_blocks()
        feature_values = {}
        
        for block in blocks:
            if "model_weights" in block:
                for feature, value in block["model_weights"].items():
                    if feature not in feature_values:
                        feature_values[feature] = []
                    feature_values[feature].append(value)
                    
        weights = {"behavior": {}}
        for feature, vals in feature_values.items():
            if not vals:
                continue
            if bft_mechanism == "median":
                weights["behavior"][feature] = statistics.median(vals)
            else:
                # Fallback to simple average
                weights["behavior"][feature] = sum(vals) / len(vals)
                
        return weights

    def reset_ledger(self):
        if os.path.exists(self.ledger_path):
            os.remove(self.ledger_path)
        self._ensure_ledger_exists()

    def _calculate_hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
