import datetime
import math
from collections import Counter

class DigitalTwin:
    def __init__(self, user_id):
        self.user_id = user_id
        # The "State Vector" - lightweight summary
        self.profile = {
            "avg_amount": 0.0,
            "std_dev_amount": 0.0,
            "m2": 0.0, # Used for Welford's algorithm to compute variance
            "transaction_count": 0,
            "frequent_locations": Counter(), # (city, country) -> count
            "frequent_categories": Counter(), # category -> count
            "frequent_merchants": Counter(), # merchant -> count
            "last_transaction_time": None,
            "last_location": None,
            "last_location_coords": None, # (lat, lon)
            "night_txn_count": 0
        }
        # In-memory history (limited size) for recent context
        # In-memory history (limited size) for recent context
        self.history = []
        self.HISTORY_LIMIT = 20
        
        # Level 2: Sequence Modeling (Markov Chain)
        self.transition_probs = {} 
        self.last_category = None

        # Personal Trusted List (Not the Social Graph)
        self.trusted_recipients = set()

    def update_state(self, transaction):
        """
        Updates the Twin's internal state with a new LEGITIMATE transaction.
        We only update state on non-fraud (or assumed legit) transactions.
        """
        amt = transaction.get("amount", 0.0)
        loc = (transaction.get("city"), transaction.get("country"))
        coords = (transaction.get("lat"), transaction.get("lon"))
        cat = transaction.get("category")
        timestamp = transaction.get("timestamp")

        # Update Statistics (Running Average & Std Dev)
        # using Welford's online algorithm for variance is better, but simple simplified here
        count = self.profile["transaction_count"]
        old_mean = self.profile["avg_amount"]
        
        new_count = count + 1
        new_mean = old_mean + (amt - old_mean) / new_count
        
        if new_count > 1:
            # Welford's algorithm for online variance
            self.profile["m2"] += (amt - old_mean) * (amt - new_mean)
            variance = self.profile["m2"] / new_count
            self.profile["std_dev_amount"] = math.sqrt(variance)

        self.profile["transaction_count"] = new_count
        self.profile["avg_amount"] = new_mean
        
        # Update Frequencies
        self.profile["frequent_locations"][loc] += 1
        self.profile["frequent_categories"][cat] += 1
        self.profile["frequent_merchants"][transaction.get("merchant")] += 1
        
        is_night = transaction.get("is_night_txn")
        if is_night is None and timestamp:
            try:
                # If timestamp is a string, handle it
                if isinstance(timestamp, str):
                    dt = datetime.datetime.fromisoformat(timestamp.replace('Z', ''))
                else:
                    dt = timestamp
                is_night = dt.hour >= 22 or dt.hour <= 6
            except:
                is_night = False
        
        if is_night:
            self.profile["night_txn_count"] += 1
        
        # Update Last Seen
        self.profile["last_transaction_time"] = timestamp
        self.profile["last_location"] = loc
        if coords[0] is not None:
             self.profile["last_location_coords"] = coords

        # Update Markov Chain (Sequence)
        if self.last_category and cat:
            if self.last_category not in self.transition_probs:
                self.transition_probs[self.last_category] = Counter()
            self.transition_probs[self.last_category][cat] += 1
        
        self.last_category = cat

        # Update Trusted List (if it's a transfer)
        if transaction.get("type") == "transfer":
            recipient = transaction.get("recipient_id")
            if recipient:
                self.trusted_recipients.add(recipient)

        # Update History
        self.history.append(transaction)
        if len(self.history) > self.HISTORY_LIMIT:
            self.history.pop(0)

    def evaluate(self, transaction, global_weights=None):
        """
        Calculates a 'Deviation Score' for a new transaction.
        Returns: (risk_score (0.0-1.0), reasons (list))
        """
        txn_count = self.profile["transaction_count"]
        # GRACE PERIOD: First few transactions are "learning only" mostly
        is_grace_period = txn_count < 5
        
        if txn_count < 1:
            return 0.0, ["First Transaction - Baseline Initialization"]

        score = 0.0
        reasons = []

        # --- STEP 1: Federated Behavioral Wisdom (Model Weights) ---
        if global_weights:
            behavioral_trends = global_weights.get("behavior", {})
            if behavioral_trends:
                # 1. Global Amount Trend (Threshold increased to ₹15,000)
                if transaction.get("amount", 0) > 10000:
                    weight = behavioral_trends.get("high_amount_trend", 0.7)
                    if weight > 0.6: # Lowered from 0.6 to match simulated global weights
                        score += 0.4
                        reasons.append(f"🌐 FEDERATED ALERT: Global trend of high-amount attacks (+0.4)")
                
                # 2. Global Night-Time Trend
                is_night = transaction.get("is_night_txn", False)
                if is_night:
                    weight = behavioral_trends.get("unusual_time_trend", 0.8)
                    if weight > 0.6: # Lowered from 0.5
                        score += 0.4
                        reasons.append(f"🌐 FEDERATED ALERT: Industry-wide spike in late-night fraud (+0.4)")

        # --- STEP 2: Local Digital Twin Analysis ---
        # 1. Amount Deviation
        amt = transaction.get("amount", 0.0)
        avg = self.profile["avg_amount"]
        
        # If amount is extreme, we flag even during grace period
        if amt > avg * 10:
            score += 0.8
            reasons.append(f"CRITICAL: Amount ₹{amt:.2f} is > 10x user average")
        elif not is_grace_period:
            if amt > avg * 5:
                score += 0.5
                reasons.append(f"Amount ₹{amt:.2f} is > 5x user average (₹{avg:.2f})")
            elif amt > avg * 3:
                score += 0.3
                reasons.append(f"Amount ₹{amt:.2f} is > 3x user average")

        # 2. Location Deviation
        loc = (transaction.get("city"), transaction.get("country"))
        top_locs = [l[0] for l in self.profile["frequent_locations"].most_common(5)]
        
        # In Grace Period, we are more lenient with locations
        if loc not in top_locs:
            loc_penalty = 0.05 if is_grace_period else 0.2
            score += loc_penalty
            if not is_grace_period:
                reasons.append(f"Location {loc} is unusual")
            
            # Impossible travel check (Physical reality still applies in grace period)
            last_loc = self.profile["last_location"]
            last_time = self.profile["last_transaction_time"]
            curr_time = transaction.get("timestamp")
            
            if last_loc and last_loc != loc and last_time:
                # Ensure timestamps are datetime objects
                t1 = last_time
                t2 = curr_time
                if isinstance(t1, str):
                    try: t1 = datetime.datetime.fromisoformat(t1.replace('Z', ''))
                    except: pass
                if isinstance(t2, str):
                    try: t2 = datetime.datetime.fromisoformat(t2.replace('Z', ''))
                    except: pass
                
                if isinstance(t1, datetime.datetime) and isinstance(t2, datetime.datetime):
                    if last_loc[1] != loc[1]:
                         time_diff = (t2 - t1).total_seconds() / 3600
                         if time_diff < 4:
                              score += 0.7 
                              reasons.append(f"Impossible travel: {last_loc[1]} to {loc[1]} in {time_diff:.1f} hrs")

        # 3. Category Deviation
        cat = transaction.get("category")
        top_cats = [c[0] for c in self.profile["frequent_categories"].most_common(5)]
        if cat not in top_cats:
            if not is_grace_period:
                score += 0.10
                reasons.append(f"New spending category: '{cat}'")
            else:
                score += 0.05

        # 4. Sequence Deviation (Markov Chain)
        # Skip sequence checks during grace period (need data)
        if not is_grace_period and self.last_category and cat and self.last_category in self.transition_probs:
            transitions = self.transition_probs[self.last_category]
            total_seen = sum(transitions.values())
            count_seen = transitions[cat]
            prob = count_seen / total_seen if total_seen > 0 else 0.0
            
            if total_seen > 3 and prob < 0.1:
                score += 0.2
                reasons.append(f"Unusual Sequence: '{self.last_category}' -> '{cat}'")

        # 5. Social Deviation (Trusted Recipients)
        if transaction.get("type") == "transfer":
            recipient = transaction.get("recipient_id")
            if recipient and recipient not in self.trusted_recipients:
                # Transfer to new person is always a bit risky
                score += 0.4
                reasons.append(f"New Recipient: {recipient} is not on your trusted list")

        return min(score, 1.0), reasons
